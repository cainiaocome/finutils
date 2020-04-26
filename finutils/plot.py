#!/usr/bin/env python

def price_volume_plot(df, price_col_name='price', volume_col_name='volume'):
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    plt.style.use('ggplot')

    data = df
    
    fig, ax = plt.subplots(nrows=2, sharex=True, figsize=(15,8))

    ax[0].plot(data.index, data[price_col_name])
    ax[1].bar(data.index, data[volume_col_name], width=1/(20*len(data.index)))

    xfmt = mpl.dates.DateFormatter('%H:%M')
    ax[1].xaxis.set_major_locator(mpl.dates.HourLocator(interval=3))
    ax[1].xaxis.set_major_formatter(xfmt)

    ax[1].xaxis.set_minor_locator(mpl.dates.HourLocator(interval=1))
    ax[1].xaxis.set_minor_formatter(xfmt)

    ax[1].get_xaxis().set_tick_params(which='major', pad=25)

    fig.autofmt_xdate()
    plt.show()

def plot_series_cdf(s, *args, **kwargs):
    from thinkstats2 import thinkstats2, thinkplot
    cdf = thinkstats2.Cdf(s)
    _  = thinkplot.Cdf(cdf)
    _ = thinkplot.Config(*args, **kwargs)
    _ = thinkplot.Show()
