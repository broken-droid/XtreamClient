<!-- markdownlint-disable -->

<div align="center"><a href='https://ko-fi.com/X8X81ELTUM' target='_blank' class="centered-image"><img height='45' style='border:0px;height:45px;' src='https://storage.ko-fi.com/cdn/kofi5.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com'/></a></div>

<a href="xtreamclient.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `xtreamclient.py`







Client class to use Xtream API. 

Connect to a server using Xtream API, authorize, get user and server information, get live/vod/series information, get categories, get epgs, download a playlist or build one from JSON data. 

<a href="xtreamclient.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `XtreamClient.__init__`

```python
__init__(
    url: str,
    username: str,
    password: str,
    headers: Optional[Dict[str, str]] = None
) → None
```

__init__ method to initialize the client. 

Set up request session and instance variables. 



**Args:**
 
 - <b>`server_url`</b> (str):   Required server url. 
 - <b>`username`</b> (str):   Required username. 
 - <b>`password`</b> (str):   Required password. 
 - <b>`headers`</b> (dict, optional):  Optional headers to pass to requests.  Default headers are set to a browser user agent. 

TODO: m3u8 playlists? 


---

#### <kbd>property</kbd> XtreamClient.allowed_output_formats

List output formats allowed by the server. 



**Returns:**
 
 - <b>`List[str]`</b>:  List of output formats 

---

#### <kbd>property</kbd> XtreamClient.headers

Headers used by this XC instance in http requests 



**Returns:**
 
 - <b>`Params`</b>:  a dictionary to use for headers in an http request 

---

#### <kbd>property</kbd> XtreamClient.output_type

Stream output format for live streams, either '' or one of the valid types allowed by the server. 



**Returns:**
 
 - <b>`str`</b>:  the current output_type for this XC instance 

---

#### <kbd>property</kbd> XtreamClient.password

Password used by this XC instance 



**Returns:**
 
 - <b>`str`</b>:  the password used by this XC instance 

---

#### <kbd>property</kbd> XtreamClient.playlist_type

Playlist type to create, either 'm3u' or 'm3u_plus'  Only creating m3u for now. 



**Returns:**
 
 - <b>`str`</b>:  the current playlist_type for this XC instance 

---

#### <kbd>property</kbd> XtreamClient.server_info

Server Info.  Contains the server_info data obtained during authorization. No setter defined, only auth sets this. 



**Raises:**
 
 - <b>`XCAuthError`</b>:  if auth fails 



**Returns:**
 
 - <b>`JSON`</b>:  dictionary of server_info data 

---

#### <kbd>property</kbd> XtreamClient.server_url

Server url used by this XC instance 



**Returns:**
 
 - <b>`str`</b>:  the server url being used by this XC instance 

---

#### <kbd>property</kbd> XtreamClient.user_info

User info from the server.  Contains the user_info data obtained during authorization. No setter defined, only auth sets this. 



**Raises:**
 
 - <b>`XCAuthError`</b>:  If auth fails 



**Returns:**
 
 - <b>`JSON`</b>:  a dictionary with the user info from the server 

---

#### <kbd>property</kbd> XtreamClient.username

Username used by this XC instance 



**Returns:**
 
 - <b>`str`</b>:  the username being used by this XC instance 



---

<a href="xtreamclient.py#L285"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `XtreamClient.auth`

```python
auth() → bool
```

Basic request to get user and server info. 



**Returns:**
 
 - <b>`bool`</b>:  True if successful 

---

<a href="xtreamclient.py#L676"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `XtreamClient.build_m3u_from_category`

```python
build_m3u_from_category(
    category: Dict[str, Any],
    file_path: str | None = None,
    tvg_chno: int | None = None,
    include_extm3u: bool | None = False
) → List[str]
```

Build an m3u from a single category.  Optionally includes #EXTM3U line at the beginning. 



**Args:**
 
 - <b>`category`</b> (JSON):  JSON data with category information.  A single item from what you would receive from get_categories. 
 - <b>`file_path`</b> (str):  Optional file path to save playlist to. 
 - <b>`tvg_chno`</b> (int | None, optional):  Optional channel number to start numbering from if using tvg-chno. Defaults to None. 
 - <b>`include_extm3u`</b> (bool | None, optional):  Includes #EXTM3U line at the beginning of the playlist. Defaults to False. 



**Returns:**
 
 - <b>`List[str]`</b>:  m3u data as a list of strings 

---

<a href="xtreamclient.py#L704"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `XtreamClient.build_m3u_from_json`

```python
build_m3u_from_json(
    file_path: str | None = None,
    live: bool | None = False,
    vod: bool | None = False,
    series: bool | None = False,
    tvg_chno: int | None = None,
    include_extm3u: bool | None = True
) → List[str]
```

Build and optionally write an m3u from JSON data from the server.  Proceeds by category, no other sorting is done. Optionally includes #EXTM3U line at the beginning.  If no stream types are selected, defaults to live streams. 



**Args:**
 
 - <b>`file_path`</b> (str | None, optional):  Write m3u to this path if provided. Defaults to None. 
 - <b>`live`</b> (bool | None, optional):  Get all live streams. Defaults to False. 
 - <b>`vod`</b> (bool | None, optional):  Get all vod streams. Defaults to False. 
 - <b>`series`</b> (bool | None, optional):  Get all series streams. Defaults to False. 
 - <b>`tvg_chno`</b> (int | None, optional):  If outputting a tvg-chno field, start at this number. Defaults to None. 
 - <b>`include_extm3u`</b> (bool | None, optional):  Include the #EXTM3U line if using this to write a file. Defaults to True. 



**Raises:**
 
 - <b>`ValueError`</b>:  at least one stream type needs to be True 



**Returns:**
 
 - <b>`List[str]`</b>:  m3u data in a list of strings 

---

<a href="xtreamclient.py#L441"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `XtreamClient.get_categories`

```python
get_categories(
    live: bool | None = False,
    vod: bool | None = False,
    series: bool | None = False
) → List[Dict[str, Any]]
```

Get Live, VOD, and/or Series categories.  You can combine multiple types in one call.  Returns Live categories by default. 



**Args:**
 
 - <b>`live`</b> (bool | None, optional):  Get live categories. Defaults to True. 
 - <b>`vod`</b> (bool | None, optional):  Get vod categories. Defaults to False. 
 - <b>`series`</b> (bool | None, optional):  Get series categories. Defaults to False. 



**Raises:**
 
 - <b>`ValueError`</b>:  if no category types are selected 



**Returns:**
 
 - <b>`List[JSON]`</b>:  List of JSON data for categories 

---

<a href="xtreamclient.py#L561"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `XtreamClient.get_epg`

```python
get_epg(stream_id: int | str | None = None) → Dict[str, Any]
```

Get EPG data for all streams, or for a specific stream with stream_id. 

Not sure if this is widely used.  Use get_xmltv if needed. 



**Args:**
 
 - <b>`stream_id`</b> (int | str | None, optional):  Optional stream id to use. Defaults to None. 



**Returns:**
 
 - <b>`JSON`</b>:  JSON data for the streams 

---

<a href="xtreamclient.py#L519"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `XtreamClient.get_info`

```python
get_info(
    stream_id: int | str,
    vod: bool | None = None,
    series: bool | None = None
) → Dict[str, Any]
```

Get info for a VOD or Series id 



**Args:**
 
 - <b>`stream_id`</b> (int | str):  stream id to get info for 
 - <b>`vod`</b> (bool):  use stream_id to get vod info 
 - <b>`series`</b> (bool):  use stream_id to get series info 



**Raises:**
 
 - <b>`ValueError`</b>:  invalid or missing arguments 



**Returns:**
 
 - <b>`JSON`</b>:  JSON data for the stream id 

---

<a href="xtreamclient.py#L580"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `XtreamClient.get_m3u`

```python
get_m3u(file_path: str | None = None) → str
```

Get m3u from the server, and save to file path if provided. 

This endpoint might be missing.  Be ready for errors. 



**Args:**
 
 - <b>`file_path`</b> (str | None, optional):  Save m3u to this path if provided. Defaults to None. 



**Returns:**
 
 - <b>`str`</b>:  String containing m3u data 

---

<a href="xtreamclient.py#L429"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `XtreamClient.get_panel`

```python
get_panel() → Dict[str, Any]
```

Get panel info from panel_api endpoint 

This returns a lot of info such as user/server/stream information, but user and server info did not have as much data as an auth call.  More may be missing.  Not sure of the use case for this. 



**Returns:**
 
 - <b>`JSON`</b>:  JSON data for a lot of different things, but not as complete 

---

<a href="xtreamclient.py#L543"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `XtreamClient.get_short_epg`

```python
get_short_epg(stream_id: int | str) → Dict[str, Any]
```

Get short epg for a stream id. 

Not sure if this is widely used.  Use get_xmltv if needed. 



**Args:**
 
 - <b>`stream_id`</b> (int | str):  stream id to use 



**Returns:**
 
 - <b>`JSON`</b>:  JSON epg data 

---

<a href="xtreamclient.py#L473"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `XtreamClient.get_streams`

```python
get_streams(
    live: bool | None = None,
    vod: bool | None = False,
    series: bool | None = False,
    category_id: int | str | None = None
) → List[Dict[str, Any]]
```

Get all selected stream types from the server, optionally restricted by category. 

Gets multiple types at a time.  Defaults to live streams if no types are set to True. 



**Args:**
 
 - <b>`live`</b> (bool | None, optional):  Get Live streams. Defaults to False. 
 - <b>`vod`</b> (bool | None, optional):  Get VOD streams. Defaults to False. 
 - <b>`series`</b> (bool | None, optional):  Get Series streams. Defaults to False. 
 - <b>`category_id`</b> (int | str | None, optional):  Optional category id to get streams from. Defaults to None. 



**Raises:**
 
 - <b>`ValueError`</b>:  if both vod and series are True 



**Returns:**
 
 - <b>`List[JSON]`</b>:  List of JSON data for streams 

---

<a href="xtreamclient.py#L602"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `XtreamClient.get_xmltv`

```python
get_xmltv(file_path: str | None = None) → str
```

Get XML epg data from the server, and save to file_path if provided. 



**Args:**
 
 - <b>`file_path`</b> (str | None, optional):  Save xml to this path if provided . Defaults to None. 



**Returns:**
 
 - <b>`str`</b>:  String containing xml epg data 






## <kbd>class</kbd> `XC404Error`
Exception raised for 404 errors. 

<a href="xtreamclient.py#L764"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `XC404Error.__init__`

```python
__init__(message: str, code: int | None = None)
```









---

## <kbd>class</kbd> `XC503Error`
Exception raised for 503 errors. 

<a href="xtreamclient.py#L769"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `XC503Error.__init__`

```python
__init__(message: str, code: int | None = None)
```









---

## <kbd>class</kbd> `XCAuthError`
Exception raised for authentication errors. 

<a href="xtreamclient.py#L759"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `XCAuthError.__init__`

```python
__init__(message: str, code: int | None = None)
```










_This filefile was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
