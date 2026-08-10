from ._mediawiki import MediaWikiAPI
from ..data import FileDescriptor
from requests import Session
from typing import Iterator


class CommonsAPI(MediaWikiAPI):
    
    def __init__(self, session: Session | None = None):
        super().__init__(apiUrl='https://commons.wikimedia.org/w/api.php', session=session)


    def getFilesNotDepictingSubject(self, categoryName: str, qId: str, wholeCategory: bool = False) -> Iterator[FileDescriptor]:
        requestParams = {
            'action': 'query',
            'list': 'search',
            'srlimit': 500,
            'srnamespace': 6,  # Namespace for files
            'srsearch': f'-haswbstatement:P180={qId} incategory:"{categoryName}" filetype:bitmap',
            'format': 'json',
            'formatversion': 2,
        }

        while True:
            rawResponse = self.httpSession.get(
                self.apiUrl,
                params=requestParams,
                timeout=60,
            )
            if rawResponse.status_code == 429:
                # Too many requests - wait and try again
                delay = int(rawResponse.headers.get('Retry-After', '5'))
                print(f'Wikimedia Commons API rate limit exceeded. Retrying after {delay} seconds...')
                import time
                time.sleep(delay)
                continue

            try:
                response = rawResponse.json()
            except Exception as e:
                raise Exception(
                    'Wikimedia Commons API responded with invalid JSON (response code: ' +
                    str(rawResponse.status_code) + '). Beginning of the response: ' + rawResponse.text[:200]
                ) from e

            searchResults = response.get('query', {}).get('search', [])
            for result in searchResults:
                if 'pageid' not in result:
                    continue
                pageId = result['pageid']
                yield FileDescriptor(f'M{pageId}', result.get('title', ''))
            
            if 'continue' not in response:
                break

            requestParams['sroffset'] = response['continue'].get('sroffset', 0)

            # Normally, we should continue listing files until we reach the limit.
            # However, Depictor seems to ignore the possibility of continuation,
            # so it relies on the user coming back and running the search again
            # in modified circumstances (e.g. with more P180 set).
            if not wholeCategory:
                break
