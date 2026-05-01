# py deck

```
# Prepare coordinates for Pydeck
    for df in [subs_df, gen_df, dc_df]:
        df['lon'] = df.geometry.x
        df['lat'] = df.geometry.y

```

defining data frames , 