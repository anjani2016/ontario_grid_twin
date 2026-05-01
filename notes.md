
- EPSG:4326: This is the standard code for the WGS84 coordinate system used by GPS and web maps.


- The One-liner Version (Method Chaining)
```.subs = gpd.read_parquet('path.parquet').to_crs(epsg=4326)  ```


```
The reason your code crashes when you include lines in that specific for loop is due to a Geometry Type Mismatch.

In geospatial data, a Point (like a substation) has a single x and y coordinate. However, a LineString (like a transmission line) consists of a series of points connected together. When you call df.geometry.x on a line, Python throws an error because a line doesn't have a single "X" coordinate—it has many.

Overview of the Solution
To fix this, we need to treat lines differently than subs, gen, and dc. While points need lat/lon columns for a ScatterplotLayer, transmission lines are rendered using their full geometry in a GeoJsonLayer or PathLayer, which doesn't require separate lat and lon columns.

Development Steps:

Separate the Loop: Only loop through the datasets that are purely Point geometries.

Coordinate Extraction: Keep the lat/lon logic for substations and data centers.

Preserve Lines: Let the lines GeoDataFrame keep its native geometry without trying to extract a single x or y.
```
