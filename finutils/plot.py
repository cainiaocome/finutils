#!/usr/bin/env python

def price_volume_plot(df):
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    plt.style.use('ggplot')

    data = df
    
    fig, ax = plt.subplots(nrows=2, sharex=True, figsize=(15,8))

    ax[0].plot(data.index, data.price)
    ax[1].bar(data.index, data.volume, width=1/(5*len(data.index)))

    xfmt = mpl.dates.DateFormatter('%H:%M')
    ax[1].xaxis.set_major_locator(mpl.dates.HourLocator(interval=3))
    ax[1].xaxis.set_major_formatter(xfmt)

    ax[1].xaxis.set_minor_locator(mpl.dates.HourLocator(interval=1))
    ax[1].xaxis.set_minor_formatter(xfmt)

    ax[1].get_xaxis().set_tick_params(which='major', pad=25)

    fig.autofmt_xdate()
    plt.show()

