import numpy as np
import xarray as xr

####
# Significance testing on composite data using the bootstrap method
####
def bootstrap(climo_data, composite_data, composite_n, variable_name, sig = .01 , tail = "both" , bootstrap_n = 1000):
    """
    Find spatial significance with bootstrapping


    Parameters
    ----------
    climo_data : xarray
        Includes variables "time", "lon", "lat", and variable <variable_name>
    composite_data : xarray
        The calculated composite you would like to test. 
        Includes dimensions "lon", "lat", and variable <variable name>. 
        Must have identical spatial footprint to climo_data
    composite_n : int
        Number of timesteps in composite data
    variable_name : str
        Name of variable in climo_data dn testing_data that you would like to test
    sig : float < 1
        The significance threshold. Default is .01 meaning top or bottom 1%.
    tail : str
        Defaults to "both" meaning you want to test for significantly 
        high and significantly low values.
        Can also select "high" or "low".
    n : int
        number of bootstrapped samples
        
    Returns
    -------
    sig_xr : xarray
        Same spatial dimensions as testing_data and climo data. 
        Includes one variable "sig_stat"
        
    """
    composite_data = composite_data[variable_name]
    climo_data = climo_data[variable_name]
    
    climo_dims = np.array(climo_data.dims)
    climo_dims = climo_dims[climo_dims != "time"]
    composite_dims = np.array(composite_data.dims)
    composite_dims = composite_dims[composite_dims != "time"]
    
    if np.all(composite_dims != climo_dims[climo_dims != "time"]):
        print("Dimensions of climo_data and composite_data are not identical.")

    if np.all(np.array(climo_data["lon"]) != np.array(composite_data["lon"])):
        print("Longitudes in climo_data and composite_data are not identical.")
    if np.all(np.array(climo_data["lat"]) != np.array(composite_data["lat"])):
        print("Latitudes in climo_data and composite_data are not identical.")
        
        
    list = []
    for i in range(bootstrap_n):
        sample_mean = climo_data.isel(time = np.random.choice(np.arange(len(climo_data.time)), size = composite_n, replace = True))
        sample_mean = sample_mean.mean(dim = 'time').load()
        
        list.append(xr.DataArray(sample_mean, dims = ['lat','lon'], 
                             coords = dict(lat = np.array(climo_data["lat"]), 
                                           lon= np.array(climo_data["lon"]),
                                           sample = i 
                                          )))
    sampled_xr = xr.concat(list, dim = 'sample')
    
    top_cutoff = np.array(sampled_xr.quantile(1-sig, dim = 'sample'))
    bottom_cutoff = np.array(sampled_xr.quantile(sig, dim = 'sample'))

    composite_sig = np.zeros((len(composite_data.lat), len(composite_data.lon)))

    composite_sig[composite_data>top_cutoff]=1
    composite_sig[composite_data<bottom_cutoff]=-1
    
    sig_xr = xr.DataArray(composite_sig, dims = ['lat','lon'], coords = dict(lat=np.array(climo_data["lat"]), lon = np.array(climo_data["lon"])))

    return(sig_xr)
