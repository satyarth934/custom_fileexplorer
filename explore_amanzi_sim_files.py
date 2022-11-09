import logging
import numpy as np
import pandas as pd
# import tkinter
# from tkinter import filedialog
import custom_file_explorer as cfe


def nad832srs(y, x):
    yu = y
    xu = x

    # SRS reference point:  
    # FSB95DR
    ys0 = 22857.47016
    xs0 = 15238.7808

    # FSB110D
    ys1 = 22614.11784
    xs1 = 15283.15968

    # UTM27 reference point:
    # FSB95DR
    y0 = 3681589.89
    x0 = 436595.57

    # FSB110D
    y1 = 3681419.31
    x1 = 436774.62

    # Angle
    y = ys1-ys0
    x = xs1-xs0
    n = y1-y0
    e = x1-x0

    cosq = ((e*x) + (n*y))/((n**2) + (e**2))
    sinq = ((n*x) - (e*y))/((n**2) + (e**2))

    # For an arbitrary UTM83 coordinate (x, y),
    # we want to have Savannah coordinate (xu, yu)
    xu = xu - x0
    yu = yu - y0

    xs = (xu*cosq) + (yu*sinq) + xs0
    ys =-(xu*sinq) + (yu*cosq) + ys0

    return (ys, xs)


def obsplot():
    filepath = "/Users/satyarth/Projects/LBNL/Haruko/utm_obs_plot/F-area_Well_Locations_Updated.csv"
    df = pd.read_csv(filepath)

    # # Selecting sites containing "D" in the site ID (lower aquifer layers)
    # df_D_bool = df.station_id.apply(lambda sid: "D" in sid)
    # df_D = df[df_D_bool]

    # List of new sensor location station IDs
    new_sensor_locs_filepath = "/Users/satyarth/Projects/LBNL/Haruko/utm_obs_plot/new_sensor_locations.csv"
    ns_df = pd.read_csv(new_sensor_locs_filepath)
    df_ns_bool = df.station_id.apply(lambda sid: sid in list(ns_df.sites))
    df_queried = df[df_ns_bool]

    ys, xs = nad832srs(y=df_queried.northing, x=df_queried.easting)

    return (xs, ys)


def read_and_plot_amanzi_lgroups(filepath, ax):
    ax.clear()

    parq_pd = pd.read_parquet(filepath, engine='pyarrow')

    tconc_colname = None
    for col_i in parq_pd.columns:
        if "total_component_concentration.cell.Tritium conc" in col_i:
            tconc_colname = col_i

    if tconc_colname is None:
        logging.warning(f"Tritium conc not available for {filepath}. Ignoring the plot.")
        return None, None

    ax.scatter(parq_pd.x, parq_pd.y, c=parq_pd[tconc_colname])
    
    # Plotting concentration for the observation data
    xs, ys = obsplot()

    # breakpoint()

    obs_tconc = list()
    for xsi, ysi in zip(xs, ys):
        shortest_dist = ((parq_pd.x - xsi)**2 + (parq_pd.y - ysi)**2)
        obs_tconc.append(parq_pd[tconc_colname].iloc[shortest_dist.argsort()[0]])

    obs_conc_scatter = ax.scatter(xs, ys, c=obs_tconc, edgecolors='red')
    # ax.get_figure().colorbar(obs_conc_scatter, ax=ax, orientation="vertical")

    return parq_pd, ax


def main():
    app = cfe.App(
        read_and_plot_func=read_and_plot_amanzi_lgroups, 
        figsize=(10, 5),
    )
    app.mainloop()


if __name__ == "__main__":
    main()