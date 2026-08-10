from requests import Session


class MediaWikiAPI:

    def __init__(self, apiUrl: str, session: Session | None = None):
        self.apiUrl = apiUrl
        self.httpSession = session if session is not None else Session()


    def login(self, username: str, password: str) -> None:
        # Step 1: Get login token
        requestParams = {
            'action': 'query',
            'meta': 'tokens',
            'type': 'login',
            'format': 'json',
        }
        response = self.httpSession.get(
            self.apiUrl,
            params=requestParams,
            timeout=60,
        )
        responseData = response.json()
        loginToken = responseData['query']['tokens']['logintoken']

        # Step 2: Perform login
        requestParams = {
            'action': 'login',
            'lgname': username,
            'lgpassword': password,
            'lgtoken': loginToken,
            'format': 'json',
        }
        response = self.httpSession.post(
            self.apiUrl,
            data=requestParams,
            timeout=60,
        )
        responseData = response.json()
        if responseData['login']['result'] != 'Success':
            raise Exception(f"Login failed: {responseData['login']['result']}")
