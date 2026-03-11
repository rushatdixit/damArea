import sys
from fetch_dam.get_dam import dam_name_to_coords
f = dam_name_to_coords("Panshet Dam")
print(f.bbox)
