# -*- encoding: utf-8 -*-

# Dissemin: open access policy enforcement tool
# Copyright (C) 2014 Antonin Delpeuch
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#



import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from jsonview.decorators import json_view
from jsonview.exceptions import BadRequest
from papers.baremodels import BareName
from papers.baremodels import BarePaper
from papers.bibtex import format_paper_citation_dict
from papers.errors import MetadataSourceException
from papers.models import Paper
from papers.name import parse_comma_name
from papers.utils import tolerant_datestamp_to_datetime
from papers.views import PaperSearchView, ResearcherView
from ratelimit.decorators import ratelimit

def api_paper_common(request, paper):
    if 'format' in request.GET and request.GET['format'] == 'bibtex':
        response = HttpResponse(paper.bibtex(), content_type='application/x-bibtex')
        response['Content-Disposition'] = 'attachement; filename={}.bib'.format(paper.slug)
        return response
    else:
        return JsonResponse({
            'status': 'ok',
            'paper': paper.json()
        })

@ratelimit(key='ip',rate='300/m', block=True)
def api_paper_pk(request, pk):
    p = Paper.objects.filter(pk=pk).first()
    if p is None:
        return JsonResponse({
            'error': 404,
            'message': 'The paper you requested could not be found.',
        }, status=404)
    return api_paper_common(request, p)

@ratelimit(key='ip',rate='300/m', block=True)
def api_paper_doi(request, doi):
    p = None
    try:
        p = Paper.get_by_doi(doi)
        if not p:
            p = Paper.create_by_doi(doi)
    except MetadataSourceException:
        pass
    if p is None:
        return JsonResponse({
            'error': 404,
            'message': 'The paper you requested could not be found.',
        }, status=404)

    return api_paper_common(request, p)


class PaperSearchAPI(PaperSearchView):
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(PaperSearchAPI, self).dispatch(*args, **kwargs)

    def render_to_response(self, context, **kwargs):
        if 'format' in self.request.GET and self.request.GET['format'] == 'bibtex':
            bibtex = format_paper_citation_dict(
                [
                    r.object.citation_dict()
                    for r in sorted(
                        context['object_list'],
                        key=lambda x: (x.object.pubdate, x.object.title)
                    )
                ],
                indent='  '
            )
            return HttpResponse(bibtex, content_type='application/x-bibtex')
        else:
            stats = context['search_stats'].pie_data()
            papers = [
                result.object.json()
                for result in context['object_list']
            ]
            messages = [m.serialize_to_json() for m in context.get('messages', [])]
            response = {
                'messages': messages,
                'stats': stats,
                'nb_results': context['nb_results'],
                'papers': papers,
            }
            return JsonResponse(response)


class ResearcherAPI(ResearcherView):
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(ResearcherAPI, self).dispatch(*args, **kwargs)

    def render_to_response(self, context, **kwargs):
        if 'format' in self.request.GET and self.request.GET['format'] == 'bibtex':
            bibtex = format_paper_citation_dict(
                [
                    r.object.citation_dict()
                    for r in sorted(
                        context['object_list'],
                        key=lambda x: (x.object.pubdate, x.object.title)
                    )
                ],
                indent='  '
            )
            return HttpResponse(bibtex, content_type='application/x-bibtex')
        else:
            # TODO: Export the full researcher object (not just the papers) as
            # JSON?
            stats = context['search_stats'].pie_data()
            papers = [
                result.object.json()
                for result in context['object_list']
            ]
            response = {
                'messages': context['messages'],
                'stats': stats,
                'nb_results': context['nb_results'],
                'papers': papers,
            }
            return JsonResponse(response)


@json_view
@csrf_exempt
@require_POST
@ratelimit(key='ip',rate='300/m', block=True)
def api_paper_query(request):
    try:
        fields = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        raise BadRequest('Invalid JSON payload')

    doi = fields.get('doi')
    if doi:
        p = None
        try:
            p = Paper.get_by_doi(doi)
            if not p:
                p = Paper.create_by_doi(doi)
        except MetadataSourceException:
            pass
        if p is None:
            raise BadRequest('Could not find a paper with this DOI')
        return {'status': 'ok', 'paper': p.json()}

    title = fields.get('title')
    if not isinstance(title,  str) or not title or len(title) > 512:
        raise BadRequest(
            'Invalid title, has to be a non-empty string shorter than 512 characters')

    date = fields.get('date')
    if not isinstance(date, str):
        raise BadRequest('A date is required')
    try:
        date = tolerant_datestamp_to_datetime(date)
    except ValueError as e:
        raise BadRequest(str(e))

    authors = fields.get('authors')
    if not isinstance(authors, list):
        raise BadRequest('A list of authors is expected')

    parsed_authors = []
    for a in authors:
        author = None
        if not isinstance(a, dict):
            raise BadRequest('Invalid author')

        if 'first' in a and 'last' in a:
            if not isinstance(a['first'], str) or not isinstance(a['last'], str) or not a['last']:
                raise BadRequest('Invalid (first,last) name provided')
            else:
                author = (a['first'], a['last'])
        elif 'plain' in a:
            if not isinstance(a['plain'], str) or not a['plain']:
                raise BadRequest('Invalid plain name provided')
            else:
                author = parse_comma_name(a['plain'])

        if author is None:
            raise BadRequest('Invalid author')

        parsed_authors.append(BareName.create(author[0], author[1]))

    if not authors:
        raise BadRequest('No authors provided')

    try:
        # Validate the metadata against our data model,
        # and compute the fingerprint to look up the paper in the DB.
        # This does NOT create a paper in the database - we do not want
        # to create papers for every search query we get!
        p = BarePaper.create(title, parsed_authors, date)
    except ValueError as e:
        raise BadRequest('Invalid paper: {}'.format(e))

    try:
        model_paper = Paper.objects.get(fingerprint=p.fingerprint)
        return {'status': 'ok', 'paper': model_paper.json()}
    except Paper.DoesNotExist:
        return {'status': 'not found'}, 404
