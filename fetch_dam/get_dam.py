import requests # type: ignore
from sentinelhub import BBox, CRS

def dam_name_to_coords(dam_name):
    """
    Converts a dam name to latitude, longitude and bounding box
    (Smallest rectangle which encloses an object)
    :param dam_name: Dam name as a string
    Uses openstreetmap to search the database for our input
    """
    url = "https://nominatim.openstreetmap.org/search"
    #the database
    queries = {
        f"{dam_name} Dam",
        f"{dam_name} Reservoir",
        dam_name,
        f"{dam_name.split()[0]} Dam" #first word + dam
    }
    for query in queries:
        params = {
            "q": query,
            #if user searchs "Khadakwasla", we search khadakwasla dam
            "format": "json",
            #returns data in terms of json, which is easier for python to read
            "limit": 1,
            #give me the best match
            "countrycodes": "in"
            #added for debugging
        }
        #https://nominatim.openstreetmap.org/search?q=Bhakra+Nangal+dam&format=json&limit=1
        #this is the equivalent url ^^^
        headers = {
            "User-Agent": "DamAreaMeasure/0.1 (research project)"
            #tells the server who you are 
        }
        response = requests.get(url, params=params, headers=headers)
        #url + params are sent to server
        #server replies with data in json format
        print("Searching for:", params["q"])
        #added so that we would know whats getting searched
        response.raise_for_status()
        #safety check
        #pushes error if response between 400 or 500
        data = response.json()
        #converts json to python list
        print("Raw response: ", data)
        #added for debugging
        if len(data) > 0:
            result = data[0]
            #it is a dict since json is a dict of dicts
            #we asked for limit = 1, so first result is the best match
            lat = float(result["lat"])
            lon = float(result["lon"])
            #lat lon contained in the dict named result
            bbox = [float(x) for x in result["boundingbox"]]
            #coordinates of vertices of bounding box
            #returns a dict of lat lon bbox
            return {
                "latitude": lat,
                "longitude": lon,
                "bounding_box": bbox
            }
    raise ValueError("Dam not found using any query strategy")
    return

def dam_name_to_bbox(name: str) -> BBox:
    result = dam_name_to_coords(name)

    bb = result["bounding_box"]

    min_lat = float(bb[0])
    max_lat = float(bb[1])
    min_lon = float(bb[2])
    max_lon = float(bb[3])

    return BBox(
        bbox=[min_lon, min_lat, max_lon, max_lat],
        crs=CRS.WGS84
    )
