# Cortex API
This is an implementation of the rest api allowing to query the database of users.

The endpoints are well documented in the usage of python -m cortex.cli.

## Return Values
Most API endpoints return a json.
Note that data results are NOT json, and are indeed full files or bson data.

### color_image
The color image returns as a url, and following the url leads to image data.

### depth_image 
The depth image returns a bson containing both raw data, and a graphical representation as an image.   
