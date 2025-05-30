import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from typing import List, Dict, Literal, Any, cast
from time import sleep
import validators

JSON = Dict[str, Any] # type for json dicts
Params = Dict[str, str] # type for request parameters

class XtreamClient:
    '''
    Client class to use Xtream API.

    Connect to a server using Xtream API, authorize, get user and server information, get live/vod/series
    information, get categories, get epgs, download a playlist or build one from JSON data.
   '''
    _outputs = {'ts': 'mpegts', 'rtmp': 'rtmp', 'm3u8': 'm3u8'} # type strings to build playlist
    # 'User-Agent': 'TiviMate/5.1.6 (Android 12)'
    # 'User-Agent': 'VLC/3.0.21 LibVLC 3.0.21'
    _class_headers = { # default class headers
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    _rq_timeout = 6 # request timeout seconds
    _forcelist = [408,429,500,502,503,504] # http status codes to retry
    _allowed_methods = ['GET'] # http request methods to retry
    _retryClass = None # reference to retry class instance

    def __init__(self, url: str, username: str, password: str, headers: Params|None=None) -> None:
        '''__init__ method to initialize the client.

        Set up request session and instance variables.

        Args:
            server_url (str):  Required server url.
            username (str):  Required username.
            password (str):  Required password.
            headers (Params | None, optional): Optional headers to pass to requests.  Default headers are set to a browser user agent.
        
        TODO: m3u8 playlists?, retry error handling may need more work
        '''
#        self.__session = self._session # initialize session
        self.server_url = url.rstrip('/') # chop off / on the end of url string if it's there
        if not validators.url(url): # basic url validator
            raise ValueError('Invalid URL')
        self.username = username
        self.password = password
        self.headers = headers # use default class headers if invalid
        self.playlist_type = 'm3u' # default to m3u type
        self.output_type = '' # allowed output types, default '', server will list valid types after auth happens

    @property
    def _session(self) -> requests.Session:
        """Get or create the requests Session instance.
        
        Returns:
            requests.Session: The session instance for making HTTP requests
        """
        if not hasattr(self, '_session_obj') or self._session_obj is None:
            # Create new session if it doesn't exist
            self._session_obj = requests.Session()
            self._session_obj.headers = self.__class__._class_headers # type: ignore - default headers
            adapter = HTTPAdapter(max_retries=self.__class__._get_custom_retry())
            self._session_obj.mount("http://", adapter)
            self._session_obj.mount("https://", adapter)
        return self._session_obj # return singleton

    @classmethod # retry class with timeout, and status codes to handle
    def _get_custom_retry(cls) -> Retry:
        '''Make a retry class to use for a session

        Returns:
            Retry: a retry class for session
        '''
        if hasattr(cls, '_retryClass') and cls._retryClass is not None:
            return cls._retryClass # if singleton exists, return it
        class CustomRetry(Retry): # otherwise make it
            def increment(self, *args, **kwargs):
                # Get the current retry count
#                current_attempt = kwargs.get('attempt_number', 0)
                # show the status code before retrying
                if 'response' in kwargs:
                    response = kwargs['response']
                    match response.status_code:
                        case 429: # too many requests
                            print(f'{response.status_code}: Waiting for 10 seconds')
                            sleep(10) # sleep for 10 seconds
                            print('Retrying')
                        case _: # everything else
                            print(f'{response.status_code}: Retrying')
                    print(f"Retrying due to status code: {response.status_code}")
                return super().increment(*args, **kwargs)
        cls._retryClass = CustomRetry(total=4,connect=4,read=4,redirect=2,allowed_methods=cls._allowed_methods,status_forcelist=cls._forcelist,backoff_factor=1,backoff_max=12)
        return cls._retryClass # set class ref and return it

    @property
    def server_url(self) -> str:
        '''Server url used by this XC instance

        Returns:
            str: the server url being used by this XC instance
        '''
        return self._server_url

    @server_url.setter
    def server_url(self, url: str) -> None:
        '''
        Args:
            url (str): a url

        Raises:
            ValueError: If url is not valid
        '''
        if type(url) is str and validators.url(url):
            self._server_url = url # basic url validator
        else:
            raise ValueError('Url must be a string')

    @property
    def username(self) -> str:
        '''Username used by this XC instance

        Returns:
            str: the username being used by this XC instance
        '''
        return self._username

    @username.setter
    def username(self, new_name: str) -> None:
        '''
        Args:
            new_name (str): new username to use for this XC instance

        Raises:
            ValueError: if new_name is not a string
        '''
        if type(new_name) is str:
            self._username = new_name
            del self.user_info
            del self.server_info # get rid of server data
        else:
            raise ValueError('Username must be a string')

    @property
    def password(self) -> str:
        '''Password used by this XC instance

        Returns:
            str: the password used by this XC instance
        '''
        return self._password

    @password.setter
    def password(self, new_pw: str) -> None:
        '''
        Args:
            new_pw (str): new password to use

        Raises:
            ValueError: if new_pw is not a string
        '''
        if type(new_pw) is str:
            self._password = new_pw
            del self.user_info
            del self.server_info # get rid of server data
        else:
            raise ValueError('Password must be a string')

    @property
    def headers(self) -> Params:
        '''Headers used by this XC instance in http requests

        Returns:
            Params: a dictionary to use for headers in an http request
        '''
        return cast(Params,self._session.headers)

    @headers.setter
    def headers(self, new_headers: Params|None) -> None:
        '''
        Args:
            new_headers (Params | None): a new dictionary of header data to use for http requests
        '''
        if (not new_headers or # new_headers is {}/None
            (all(isinstance(key, str) for key in new_headers)) or # not all keys are strings
                (all(isinstance(value, str) for value in new_headers.values()))): # not all values are strings
            new_headers = self.__class__._class_headers # use the default class headers instead of raising an error
        self._session.headers.update(new_headers) # update session headers

    @property
    def playlist_type(self) -> str:
        '''Playlist type to create, either 'm3u' or 'm3u_plus'  Only creating m3u for now.

        Returns:
            str: the current playlist_type for this XC instance
        '''
        return self._playlist_type

    @playlist_type.setter
    def playlist_type(self, ptype: Literal['m3u', 'm3u_plus']='m3u') -> None:
        '''
        Args:
            ptype (Literal[&#39;m3u&#39;, &#39;m3u_plus&#39;], optional): A new playlist_type. Defaults to 'm3u'.
        '''
        if ptype not in ['m3u', 'm3u_plus']:
            ptype = 'm3u' # default to m3u instead of raising an error
        self._playlist_type = ptype  # Set new playlist type

    @property
    def output_type(self) -> str:
        '''Stream output format for live streams, either '' or one of the valid types allowed by the server.

        Returns:
            str: the current output_type for this XC instance
        '''
        if not hasattr(self, '_output_type') or not self._output_type:
            return '' # empty string if None or attribute doesn't exist
        return self._output_type

    @output_type.setter
    def output_type(self, otype: str) -> None:
    # X.ts,  X.m3u8, etc, server info lists valid output types for live streams.  VOD and Series have their own output types.
        '''
        Args:
            otype (str): output type, must be a type allowed by the server, or ''
        Raises:
            ValueError: if output type is not in the allowed_output_formats field
        '''
        if otype not in self.allowed_output_formats: # limit otype to valid formats
            raise ValueError(f'Valid output type needed for this server: {self.allowed_output_formats}')
        self._output_type = otype # set new output type

    @property
    def allowed_output_formats(self) -> List[str]:
        '''List output formats allowed by the server.

        Returns:
            List[str]: List of output formats
        '''
        allowed = [''] # default ''
        try:
            allowed.extend(self.user_info['allowed_output_formats']) # formats listed by server
        except XCAuthError:
            pass # not authed yet, just use default
        return allowed

    @property
    def user_info(self) -> JSON:
        '''User info from the server.  Contains the user_info data obtained during authorization.
        No setter defined, only auth sets this.

        Raises:
            XCAuthError: If auth fails

        Returns:
            JSON: a dictionary with the user info from the server
        '''
        if not self._is_authenticated: # this var won't exist if not auth'd
                raise # failed auth
        return self._user_info # return the dict with all data
    
    @user_info.deleter
    def user_info(self) -> None:
        self._delete('_user_info')
    
    @property
    def server_info(self) -> JSON:
        '''Server Info.  Contains the server_info data obtained during authorization.
        No setter defined, only auth sets this.

        Raises:
            XCAuthError: if auth fails

        Returns:
            JSON: dictionary of server_info data
        '''
        if not self._is_authenticated: # this var won't exist if not auth'd
                raise # failed auth
        return self._server_info # return the dict with all data
    
    @server_info.deleter
    def server_info(self) -> None:
        self._delete('_server_info')

    def _delete(self, attr: str) -> None:
        '''Delete an attribute, and handle errors here instead of in each delete method

        Args:
            attr (str): attribute name to delete
        '''
        try: # delete attribute, keep the error handling here
            delattr(self, attr)
        except AttributeError:
            pass # skip if it's already deleted

    @property # use this internally
    def _is_authenticated(self) -> bool:
        '''Check if 'auth' is valid, or attempt to auth if it isn't.

        Raises:
            XCAuthError: auth failed

        Returns:
            bool: True if auth succeeded, otherwise False
        '''
        if not hasattr(self, '_user_info'): # check if user info has been set
            self.auth() # attempt to auth if we haven't tried yet
        if self._user_info['auth'] == 0: # use directly to skip auth
            raise XCAuthError('Failed Authentication')
        return True

    @staticmethod
    def _pos_int(value: int|str) -> bool:
        '''Check if value is a positive integer.

        Args:
            value (int | str): a value to check

        Raises:
            ValueError: if value was not a positive integer

        Returns:
            bool: True if value was a positive integer, otherwise False
        '''
        try:
            value = int(value) # convert to int if it's not already
            if value > 0:
                value = str(value) # back to str
                return True
            raise ValueError('value must be a positive integer')
        except ValueError:
            raise # raise an error if not a positive int

    def auth(self) -> bool:
    #{server}/player_api.php?username={username}&password={password}
        '''Basic request to get user and server info.
        
        Returns:
            bool: True if successful
        '''
        result = self._make_request_json('player_api.php')
        self._server_info = result['server_info'] # save server info, set these directly
        self._user_info = result['user_info'] # save user info, set these directly
        if self._user_info['auth'] == 0: # auth failed
            return False
        return True

    def _make_request_json(self, endpoint: Literal['player_api.php', 'panel_api.php'],
                        params: Params|None = None)-> JSON:
        '''Wrapper for __make_request that returns JSON only.  Only player_api and panel_api return JSON.


        Make a request to an endpoint on the server, using the username and password set by the class instance.
        Additional parameters can be passed in the params argument.  The response is either JSON, List[JSON], or
        text, and is_json indicates which type to return.  If the request fails, an exception is raised.  Result
        is cast to JSON to make it simple for typing.

        Args:
            endpoint (Literal[&#39;player_api.php&#39;, &#39;panel_api.php&#39;]): endpoint to use in the request
            params (Params | None, optional): Additional params to use besides username and password. Defaults to None.
            is_json (bool | None, optional): Indicates what type of data to return. Defaults to True for JSON.

        Raises:
            XC404Error: if the endpoint request returned 404
            XCAuthError: if authentication failed
            XC503Error: server was temporarily busy during request
            Exception: additional unexpected/unhandled errors

        Returns:
            JSON: JSON data from the server response
        '''
        return cast(JSON,self.__make_request(endpoint,params,True)) # json wrapper, cast as json

    def _make_request_list_json(self, endpoint: Literal['player_api.php'],
                        params: Params|None = None)-> List[JSON]:
        '''Wrapper for __make_request that returns List[JSON] only.  Only player_api calls will use this, for
        get_categories, and get_streams.


        Make a request to an endpoint on the server, using the username and password set by the class instance.
        Additional parameters can be passed in the params argument.  The response is JSON, List[JSON] or text, and
        is_json indicates which type to return.  If the request fails, an exception is raised.  Result is cast
        to List[JSON] to make it simple for typing.  get_streams and get_categories will return List[JSON].

        Args:
            endpoint (Literal[&#39;player_api.php&#39;]): endpoint to use in the request
            params (Params | None, optional): Additional params to use besides username and password. Defaults to None.
            is_json (bool | None, optional): Indicates what type of data to return. Defaults to True for JSON.

        Raises:
            XC404Error: if the endpoint request returned 404
            XCAuthError: if authentication failed
            XC503Error: server was temporarily busy during request
            Exception: additional unexpected/unhandled errors

        Returns:
            JSON: JSON data from the server response
        '''
        return cast(List[JSON],self.__make_request(endpoint,params,True)) # list wrapper, cast as list of json

    def _make_request_text(self, endpoint: Literal['get.php', 'xmltv.php'],
                        params: Params|None = None)-> str:
        '''Wrapper for __make_request that returns text only.  Only get and xmltv return text.


        Make a request to an endpoint on the server, using the username and password set by the class instance.
        Additional parameters can be passed in the params argument.  The response is either JSON, List[JSON], or
        text, and is_json indicates which type to return.  If the request fails, an exception is raised.  Text
        response is cast to str to make it simple for typing.

        Args:
            endpoint (Literal[&#39;get.php&#39;, &#39;xmltv.php&#39;]): endpoint to use in the request
            params (Params | None, optional): Additional params to use besides username and password. Defaults to None.
            is_json (bool | None, optional): Indicates what type of data to return. Defaults to True for JSON.

        Raises:
            XC404Error: if the endpoint request returned 404
            XCAuthError: if authentication failed
            XC503Error: server was temporarily busy during request
            Exception: additional unexpected/unhandled errors

        Returns:
            str: text string from the server response
        '''
        return cast(str,self.__make_request(endpoint,params,False)) # text wrapper, so cast as str

    def __make_request(self, endpoint: Literal['player_api.php', 'panel_api.php', 'get.php', 'xmltv.php'],
                        params: Params|None = None, is_json: bool|None = True)-> JSON|List[JSON]|str:
        '''Make a request to an endpoint on the server.


        Make a request to an endpoint on the server, using the username and password set by the class instance.
        Additional parameters can be passed in the params argument.  The response is either JSON or text, and
        is_json indicates which type to return.  If the request fails, an exception is raised.  The JSON response
        could also be a list of JSON objects.  In most cases it will just be JSON.  Use the _make_request wrappers
        to help with typing.

        Args:
            endpoint (Literal[&#39;player_api.php&#39;, &#39;panel_api.php&#39;, &#39;get.php&#39;, &#39;xmltv.php&#39;]): endpoint to use in the request
            params (Params | None, optional): Additional params to use besides username and password. Defaults to None.
            is_json (bool | None, optional): Indicates what type of data to return. Defaults to True for JSON.

        Raises:
            XC404Error: if the endpoint request returned 404
            XCAuthError: if authentication failed
            XC503Error: server was temporarily busy during request
            Exception: additional unexpected/unhandled errors

        Returns:
            JSON|List[JSON]|str: either JSON data, List of JSON data, or a text string from the server response
        '''
        if 'player_api.php' in endpoint and not params:
            pass # this is the auth call, allow it
        elif not self._is_authenticated: # for every other call, check state first
            raise # failed auth
        url = f"{self.server_url}/{endpoint}"
        request_params: Params = {'username': self.username, 'password': self.password}
        if params is not None:
            request_params.update(params) # add additional parameters to user/pass
        try:
            response = self._session.get(url, params=request_params, timeout=self.__class__._rq_timeout) # request with params and timeout
            response.raise_for_status()
            return response.json() if is_json else response.text # return json or text
        except requests.exceptions.HTTPError as e:
            match e.response.status_code:
                case 404: # not found
                    raise XC404Error(f'Resource not found: {url}',404)
                case 444: # banned?
                    raise XCAuthError(f'Account banned or invalid: {self._username}',444)
            #     case 503: # temporarily unavailable, use a delayed retry
            #         raise XC503Error(f'Service Temporarily Unavailable',503)
                case _: # unexpected
                    raise Exception(f'Request failed: {e.response.status_code} - {e.response.reason}')

        except Exception:
            raise # raise any other unhandled error

    def get_panel(self) -> JSON:
    #{server}/panel_api.php?username={username}&password={password}
        '''Get panel info from panel_api endpoint

        This returns a lot of info such as user/server/stream information, but user and server info
        did not have as much data as an auth call.  More may be missing.  Not sure of the use case for this.

        Returns:
            JSON: JSON data for a lot of different things, but not as complete
        '''
        return self._make_request_json('panel_api.php')

    def get_categories(self, live: bool|None=False, vod: bool|None = False, series: bool|None = False) -> List[JSON]:
    #{server}/player_api.php?username={username}&password={password}&action=get_live_categories
    #{server}/player_api.php?username={username}&password={password}&action=get_vod_categories
    #{server}/player_api.php?username={username}&password={password}&action=get_series_categories
    # {'category_id': '123', 'category_name': 'Category', 'parent_id': 0}
        '''Get Live, VOD, and/or Series categories.  You can combine multiple types in one call.  Returns Live categories by default.
        
        Args:
            live (bool | None, optional): Get live categories. Defaults to True.
            vod (bool | None, optional): Get vod categories. Defaults to False.
            series (bool | None, optional): Get series categories. Defaults to False.

        Raises:
            ValueError: if no category types are selected

        Returns:
            List[JSON]: List of JSON data for categories
        '''
        if not (live or vod or series):
            live = True # if nothing is selected, default to live instead of raising an error
        categories = []
        if live: # live categories
            params: Params = {'action': 'get_live_categories'} # live categories
            categories.extend(self._make_request_list_json('player_api.php', params=params))
        if vod: # vod categories
            params: Params = {'action': 'get_vod_categories'} # vod categories
            categories.extend(self._make_request_list_json('player_api.php', params=params))
        elif series: # series categories
            params: Params = {'action': 'get_series_categories'} # series categories
            categories.extend(self._make_request_list_json('player_api.php', params=params))
        return categories # List[JSON]

    def get_streams(self, live: bool|None=None, vod: bool|None = False, series: bool|None = False, category_id: int|str|None = None) -> List[JSON]:
    #{server}/player_api.php?username={username}&password={password}&action=get_live_streams
    #{server}/player_api.php?username={username}&password={password}&action=get_vod_streams
    #{server}/player_api.php?username={username}&password={password}&action=get_series
    #{server}/player_api.php?username={username}&password={password}&action=get_live_streams&category_id=X <- optional category_id
    # return list of these:
    #{'num': 1, 'name': 'Test Name 1', 'stream_type': 'live', 'stream_id': 12345, 'stream_icon': 'https://link.url/path/img.png', 'epg_channel_id': 'testchannel1.us', 'added': '1502285791', 'category_id': '30', 'custom_sid': '', 'tv_archive': 0, 'direct_source': '', 'tv_archive_duration': 0}
        '''Get all selected stream types from the server, optionally restricted by category.
        
        Gets multiple types at a time.  Defaults to live streams if no types are set to True.

        Args:
            live (bool | None, optional): Get Live streams. Defaults to False.
            vod (bool | None, optional): Get VOD streams. Defaults to False.
            series (bool | None, optional): Get Series streams. Defaults to False.
            category_id (int | str | None, optional): Optional category id to get streams from. Defaults to None.

        Raises:
            ValueError: if both vod and series are True

        Returns:
            List[JSON]: List of JSON data for streams
        '''
        if category_id is not None and not self._pos_int(category_id):
            raise # invalid category id
        if not (live or vod or series): # if nothing is selected
            live = True # default to live streams
        params: Params = {}
        output = [] # hold streams to return
        if live: # live streams
            params['action'] = 'get_live_streams'
            if category_id is not None: # add category id parameter if it's there
                params['category_id'] = str(category_id)
            output.extend(self._make_request_list_json('player_api.php', params=params)) # List[JSON]
        if vod: # vod streams
            params['action'] = 'get_vod_streams'
            if category_id is not None: # add category id parameter if it's there
                params['category_id'] = str(category_id)
            output.extend(self._make_request_list_json('player_api.php', params=params)) # List[JSON]
        elif series: # series streams
            params['action'] = 'get_series'
            if category_id is not None: # add category id parameter if it's there
                params['category_id'] = str(category_id)
            output.extend(self._make_request_list_json('player_api.php', params=params)) # List[JSON]
        return output # List[JSON] of selected stream types

    def get_info(self, stream_id: int|str, vod: bool|None=None, series: bool|None=None) -> JSON:
    #{server}/player_api.php?username={username}&password={password}&action=get_vod_info&vod_id=X
    #{server}/player_api.php?username={username}&password={password}&action=get_series_info&series_id=X
        '''Get info for a VOD or Series id

        Args:
            stream_id (int | str): stream id to get info for
            vod (bool): use stream_id to get vod info
            series (bool): use stream_id to get series info

        Raises:
            ValueError: invalid or missing arguments

        Returns:
            JSON: JSON data for the stream id
        '''
        if not (vod or series) or not self._pos_int(stream_id): # no type selcted, or invalid stream_id
            raise ValueError('Either vod or series must be selected, and stream_id must be a positive integer')
        info_type = ''
        if vod: info_type = 'vod'
        else: info_type = 'series'
        params: Params = {'action': f'get_{info_type}_info', f'{info_type}_id': str(stream_id)}
        return self._make_request_json('player_api.php', params=params)

    def get_short_epg(self, stream_id: int|str) -> JSON:
        '''Get short epg for a stream id.

        Not sure if this is widely used.  Use get_xmltv if needed.

        Args:
            stream_id (int | str): stream id to use

        Returns:
            JSON: JSON epg data
        '''
    #{server}/player_api.php?username={username}&password={password}&action=get_short_epg&stream_id=X
        if not self._pos_int(stream_id):
            raise # stream_id not a positive integer
        params: Params = {'action': 'get_short_epg', 'stream_id': str(stream_id)}
#       json with 'epg_listings' key
        return self._make_request_json('player_api.php',params=params)['epg_listings']

    def get_epg(self, stream_id: int|str|None = None) -> JSON:
    #{server}/player_api.php?username={username}&password={password}&action=get_simple_data_table
    #{server}/player_api.php?username={username}&password={password}&action=get_simple_data_table&stream_id=X
        '''Get EPG data for all streams, or for a specific stream with stream_id.

        Not sure if this is widely used.  Use get_xmltv if needed.

        Args:
            stream_id (int | str | None, optional): Optional stream id to use. Defaults to None.

        Returns:
            JSON: JSON data for the streams
        '''
        params: Params = {'action': 'get_simple_data_table'}
        if stream_id is not None and self._pos_int(stream_id): # check if stream_id is a positive int
            params['stream_id'] = str(stream_id) # should be a string after _pos_int check
#       json with 'epg_listings' key
        return self._make_request_json('player_api.php', params)['epg_listings']

    def get_m3u(self, file_path: str|None=None) -> str:
    #{server}/get.php?username={username}&password={password}&type=m3u&output=mpegts
    #{server}/get.php?username={username}&password={password}&type=m3u_plus&output=mpegts
        '''Get m3u from the server, and save to file path if provided.

        This endpoint might be missing.  Be ready for errors.

        Args:
            file_path (str | None, optional): Save m3u to this path if provided. Defaults to None.

        Returns:
            str: String containing m3u data
        '''
        params: Params = {'type': self.playlist_type}
        if self.output_type:
            params['output'] = self.__class__._outputs[self.output_type] # get the string associated for the type
        m3u = self._make_request_text('get.php', params)
        if file_path:
            with open(file_path,'wt',encoding='utf-8') as f:
                f.write(m3u)
        return m3u

    def get_xmltv(self, file_path: str|None=None) -> str:
    #{server}/xmltv.php?username={username}&password={password}
        '''Get XML epg data from the server, and save to file_path if provided.

        Args:
            file_path (str | None, optional): Save xml to this path if provided . Defaults to None.

        Returns:
            str: String containing xml epg data
        '''
        xml = self._make_request_text('xmltv.php')
        if file_path:
            with open(file_path, 'wt') as f:
                f.write(xml)
        return xml

    def _build_extinf_line(self, stream: JSON, cat_name: str, tvg_chno: int|None=None) -> str:
        '''Build an #EXTINF line for an m3u out of a given stream and category name, with an optional channel number.

        Args:
            stream (JSON): stream JSON (dict)
            cat_name (str): category name
            tvg_chno (int | None, optional): Optional channel number. Defaults to None.

        Raises:
            ValueError: if stream type is not live/movie/series

        Returns:
            str: an #EXTINF line for a stream url
        '''
        tvg_chno_str = '' # build tvg-no if we're using it
        tvg_id_str = '' # build tvg-id, for live tv
        if tvg_chno is not None:
            tvg_chno_str = f' tvg-no="{tvg_chno}"'
        stream_type = stream['stream_type']
        match stream_type: # figure out file extension if there is one
            case 'live':
                epg_id = stream['epg_channel_id']
                if not (epg_id is None or epg_id == ''):
                    tvg_id_str = f' tvg-id="{stream["epg_channel_id"]}"' # live has epg, others do not
            case 'movie':
                pass # nothing special for movies
            case 'series':
                pass # nothing special for series
            case _:
                raise ValueError(f'Unexpected stream type for stream: {stream["stream_id"]}') # unexpected stream type
        return f'#EXTINF: -1{tvg_chno_str}{tvg_id_str} tvg-name="{stream["name"]}" tvg-logo={stream["stream_icon"]} group-title="{cat_name}",{stream["name"]}'

    def _build_stream_url(self, stream: JSON, uses_live_path: bool|None=True) -> str:
    # {self._server_url}/live/{self._username}/{self._password}/{stream_id}.{self._output_type}
        '''Create a string containing a stream url for the specified stream id.  Default behavior is to return a live stream url.
        Args:
            stream (JSON): JSON data for a stream to use to create a url
            uses_live_path (bool | None, optional): Optional bool to indicate if the live path includes /live/. Default is True.
        Returns:
            str: url for the stream id
        Raises:
            ValueError: if stream type was not live/movie/series
        '''
        output_ext = None
        stream_type = stream['stream_type']
        match stream_type: # figure out file extension if there is one
            case 'live':
                output_ext = self.output_type # output type allowed by server
            case 'movie':
                output_ext = stream['container_extension'] # movies and series have their own types, and no epg
            case 'series':
                output_ext = stream['container_extension']
            case _:
                raise ValueError(f'Unexpected stream type for stream: {stream["stream_id"]}') # unexpected stream type
        if output_ext is not None or output_ext != '': # if no extension, don't prefix with '.'
            output_ext = '.'+output_ext
        return f'{self.server_url}/{stream_type}/{self.username}/{self.password}/{stream["stream_id"]}{output_ext}'

    def build_m3u_from_category(self, category: JSON, file_path: str|None=None, tvg_chno: int|None=None, include_extm3u: bool|None=False) -> List[str]:
        '''Build an m3u from a single category.  Optionally includes #EXTM3U line at the beginning.

        Args:
            category (JSON): JSON data with category information.  A single item from what you would receive from get_categories.
            file_path (str): Optional file path to save playlist to.
            tvg_chno (int | None, optional): Optional channel number to start numbering from if using tvg-chno. Defaults to None.
            include_extm3u (bool | None, optional): Includes #EXTM3U line at the beginning of the playlist. Defaults to False.

        Returns:
            List[str]: m3u data as a list of strings
        '''
        category_id = category['category_id']
        category_name = category['category_name']
        lines: List[str] = [] # lines to return, add \n's to each line
        if include_extm3u: # include #EXTM3U line if we want to use this to write to a file
            lines = ['#EXTM3U\n']
        streams = self.get_streams(category_id=category_id)
        for stream in streams:
            lines.append(self._build_extinf_line(stream,category_name,tvg_chno)+'\n') # make #EXTINF line
            lines.append(self._build_stream_url(stream)+'\n') # make a url out of the stream
            if tvg_chno is not None:
                tvg_chno += 1 # ++ channel number
        if file_path is not None: # write to file if path provided
            with open(file_path, 'wt',encoding='utf-8') as f:
                f.writelines(lines)
        return lines

    def build_m3u_from_json(self, file_path: str|None=None, live: bool|None=False, vod: bool|None=False, series: bool|None=False, tvg_chno: int|None=None, include_extm3u: bool|None=True) -> List[str]:
        '''Build and optionally write an m3u from JSON data from the server.  Proceeds by category, no other sorting is done.
        Optionally includes #EXTM3U line at the beginning.  If no stream types are selected, defaults to live streams.

        Args:
            file_path (str | None, optional): Write m3u to this path if provided. Defaults to None.
            live (bool | None, optional): Get all live streams. Defaults to False.
            vod (bool | None, optional): Get all vod streams. Defaults to False.
            series (bool | None, optional): Get all series streams. Defaults to False.
            tvg_chno (int | None, optional): If outputting a tvg-chno field, start at this number. Defaults to None.
            include_extm3u (bool | None, optional): Include the #EXTM3U line if using this to write a file. Defaults to True.

        Raises:
            ValueError: at least one stream type needs to be True

        Returns:
            List[str]: m3u data in a list of strings
        '''
        playlist = []
        if not (live or vod or series): # need to pick at least one, more is ok
            live = True # default to live instead of raising an error if nothing is True
        if include_extm3u: # include #EXTM3U line if we want to use this to write to a file
            playlist.append('#EXTM3U\n')
        if live:
            categories = self.get_categories() # get live categories
            for category in categories:
                lines = self.build_m3u_from_category(category=category,tvg_chno=tvg_chno)
                playlist.extend(lines) # add to playlist
                if tvg_chno is not None:
                    tvg_chno += 1 # incriment channel num
        if vod:
            categories = self.get_categories(vod=True) # get vod categories
            for category in categories:
                lines = self.build_m3u_from_category(category=category,tvg_chno=tvg_chno)
                playlist.extend(lines) # add to playlist
                if tvg_chno is not None:
                    tvg_chno += 1 # incriment channel num
        if series:
            categories = self.get_categories(series=True) # get series categories
            for category in categories:
                lines = self.build_m3u_from_category(category=category,tvg_chno=tvg_chno)
                playlist.extend(lines) # add to playlist
                if tvg_chno is not None:
                    tvg_chno += 1 # incriment channel num
        try:
            if file_path:
                with open(file_path, 'wt', encoding='utf-8') as f:
                    f.writelines(playlist)
                    f.close()
        except Exception as e:
            print(e)
        return playlist

class XCAuthError(Exception): # auth failed
    '''Exception raised for authentication errors.'''
    def __init__(self, message: str, code: int|None = None):
        super().__init__(message)
        self.code = code
class XC404Error(Exception): # 404 on an endpoint, usually on playlist
    '''Exception raised for 404 errors.'''
    def __init__(self, message: str, code: int|None = None):
        super().__init__(message)
        self.code = code
class XC503Error(Exception): # 503, server temporary unavailable, retry
    '''Exception raised for 503 errors.'''
    def __init__(self, message: str, code: int|None = None):
        super().__init__(message)
        self.code = code
