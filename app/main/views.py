"""
Evert application routes are stored in this module.
"""

from flask import render_template, session, redirect, url_for, flash
from . import main
from .forms import UploadForm
from werkzeug.utils import secure_filename
from pandas import read_csv
from numpy import linspace, exp, sin, histogram, size, zeros_like
from scipy.stats import gaussian_kde as gkde
from pandas import DataFrame
from bokeh.plotting import figure, gridplot
from bokeh.embed import components
from bokeh.models import CustomJS, ColumnDataSource, Range1d, LinearAxis
from bokeh.models.tools import BoxSelectTool, PanTool, ResetTool, WheelZoomTool, BoxZoomTool



@main.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@main.route('/upload', methods=['GET', 'POST'])
def upload():
    filename = None
    form = UploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        form.file.data.save('app/static/uploads/' + filename)
        session['newUpload'] = filename  # This session library element serves to allow interactive feedback
        flash(filename + ' successfully uploaded to Evert.')
        return redirect(url_for('main.upload'))  # url_for() builds a URL to a specific function, html file irrelevant
    else:                                        # Now main.upload used as the function is relevant to a spec blueprint
        filename = None
    return render_template('upload.html', form=form)


# Try to directly embed into HTML whilst still making use of Bootstrap
@main.route('/fit', methods=['GET'])
def fit():

    # Read data as if uploaded file is now used, Data set 1
    data1 = read_csv('app/static/uploads/Data1.csv', sep=',', skipinitialspace=1)

    xdata1 = data1.values[:,1]    # Extract Data
    ydata1 = data1.values[:,2]
    colour1 = ['black']*len(xdata1)

    # Read data as if uploaded file is now used, Data set 2
    data2 = read_csv('app/static/uploads/Data2.csv', sep=',', skipinitialspace=1)

    xdata2 = data2.values[:,1]
    ydata2 = data2.values[:,2]
    colour2 = ['green']*len(xdata2)

    # Read data as if uploaded file is now used, Data set 3
    data3 = read_csv('app/static/uploads/Data3.csv', sep=',', skipinitialspace=1)

    xdata3 = data3.values[:,1]
    ydata3 = data3.values[:,2]
    colour3 = ['red']*len(xdata3)

    # Prepare Data3
    # xdata3 = linspace(0, 100, 10)
    # ydata3 = sin(10*xdata3)

    # Data_pandas = DataFrame({'Time': xdata3,
    #                        'Value': ydata3})

    # Data_pandas.to_csv('app/static/uploads/Data3.csv')


    # Assign read data to ColumnDataSource objects
    sourceData1 = ColumnDataSource(data=dict(x=xdata1, y=ydata1, color=colour1))
    sourceData2 = ColumnDataSource(data=dict(x=xdata2, y=ydata2, color=colour2))
    sourceData3 = ColumnDataSource(data=dict(x=xdata3, y=ydata3, color=colour3))

    my_plot = figure(tools=[BoxSelectTool(dimensions=['width'], select_every_mousemove=True), PanTool(), ResetTool(), WheelZoomTool(), BoxZoomTool()],
                     title='Time series data',
                     x_range=(xdata1.min(), xdata1.max()),
                     y_range=(ydata1.min(), ydata1.max()),
                     width=1200)      # Create figure object; DEBUG: select_every_mousemove=False

    my_plot.extra_y_ranges = {# 'Data1': Range1d(start=ydata1.min(), end=ydata1.max()),
                              'Data2': Range1d(start=ydata2.min(), end=ydata2.max()),
                              'Data3': Range1d(start=ydata3.min(), end=ydata3.max())}

    my_plot.circle(x='x', y='y', color='color', source=sourceData1,
                   size=8, alpha=0.8, legend='Data 1')  # Add circle elements (glyphs) to the figure

    my_plot.circle(x='x', y='y', color='color', source=sourceData2,
                   size=5, alpha=0.8, y_range_name='Data2', legend='Data 2')

    my_plot.circle(x='x', y='y', color='color', source=sourceData3,
                   size=8, alpha=0.5, y_range_name='Data3', legend='Data 3')
    my_plot.line(x='x', y='y', color='red', source= sourceData3,
                 alpha=0.5, y_range_name='Data3', legend='Data 3')


    sourceFit = ColumnDataSource(data=dict(xfit=[], yfit=[]))
    my_plot.circle(x='xfit', y='yfit', source=sourceFit, color='orange', alpha=0.3)

    # my_plot.add_layout(LinearAxis(y_range_name='Data1', axis_line_color=colour1[0]), 'left')
    my_plot.add_layout(LinearAxis(y_range_name='Data2', axis_line_color=colour2[0], axis_line_width=3), 'left')
    my_plot.add_layout(LinearAxis(y_range_name='Data3', axis_line_color=colour3[0], axis_line_width=3), 'left')


    # sourceAnnotate = ColumnDataSource(data=dict(text=['Foo', 'Bah'], x=[50, 50], y=[0.5, 0], x_offset=[0,0], y_offset=[0,0], text_font_size=['15pt', '15pt'],

    #                                            text_color=['orange', 'orange']))
    # my_plot.text(source=sourceAnnotate, text='text', x='x', y='y', x_offset='x_offset', y_offset='y_offset', text_font_size='text_font_size', text_color='text_color')

    sourceData1.callback = CustomJS(args=dict(sourceFit=sourceFit), code=("""FirstOrderEyeball(cb_obj, sourceFit)"""))

    # sourceData.callback = CustomJS(args=dict(sourceFit=sourceFit, sourceAnnotate=sourceAnnotate), code=("""FirstOrderEyeball(cb_obj, sourceFit, sourceAnnotate)"""))

    script, div = components(my_plot)  # Break figure up into component HTML to be added to template
    return render_template("int_scatter.html", myScript=script, myDiv=div)
    
@main.route("/plot")
def plot():        
    #Data import
    data_file = read_csv("app/static/uploads/LPG_Data_Set_1_n.csv", parse_dates = ['timestamp'])
    data_source = ColumnDataSource(data=dict(x = data_file['timestamp'],y1 = data_file['l1013aspv'],y2 = data_file['l1015asop']))
            
    # Figure plotting function
    def make_figure():
        #Create scatter plot of data
        #set up figure
#        plot_tools = ['wheel_zoom']
        time_plot = figure(plot_height= 400, plot_width= 800, title="", x_axis_label ='Time', 
                    tools='', y_axis_label = 'l1013aspv', toolbar_location="left",
                    x_axis_type="datetime",
                    y_range=(min(data_source.data["y1"]) -min(data_source.data["y1"]*0.1 ),
                             max(data_source.data["y1"]) + max(data_source.data["y1"]*0.1)))
                    
        #Customize time_plot grid lines
        time_plot.xgrid.grid_line_color = None
        time_plot.ygrid.grid_line_alpha = 0.2
        
        #modify the BoxSelectTool 
        #dimensions = specify the dimension in which the box selection is free in
        #select_every_mousemove = select points as box moves over
        time_plot.add_tools(BoxSelectTool(dimensions = ["width"], select_every_mousemove = True))

        #add anther axis
        time_plot.extra_y_ranges = {"foo": Range1d(start = min(data_source.data["y2"]) - min(data_source.data["y1"]*0.1),
                                                  end = max(data_source.data["y2"]) + max(data_source.data["y1"]*0.1))}
                                                  
        #add data to scatter plot (data points on time plot)
        time_scat = time_plot.scatter("x", "y1", source = data_source,size = 1, color = "green")
        time_scat2 = time_plot.scatter("x", "y2", source = data_source,size= 1, color = "blue", y_range_name = "foo")
           
        #add time series line
        time_plot.line("x","y1",source=data_source,color = time_scat.glyph.fill_color,
                                   alpha=0.5)
                                   
        time_plot.line("x","y2",source=data_source,color= time_scat2.glyph.fill_color,
                                    alpha=0.5,y_range_name="foo")   
        
        #First axes styling
        time_plot.yaxis.axis_line_color = time_scat.glyph.fill_color
        time_plot.yaxis.minor_tick_line_color = time_scat.glyph.fill_color
        time_plot.yaxis.major_tick_line_color = time_scat.glyph.fill_color
        time_plot.yaxis.axis_label_text_color = time_scat.glyph.fill_color
        time_plot.yaxis.major_label_text_color = time_scat.glyph.fill_color
        
        #add second axis to time_plot and styling
        time_plot.add_layout(LinearAxis(y_range_name = "foo",
                                        axis_line_color = str(time_scat2.glyph.fill_color),
                                        major_label_text_color = str(time_scat2.glyph.fill_color), 
                                        axis_label_text_color = str(time_scat2.glyph.fill_color),
                                        major_tick_line_color = str(time_scat2.glyph.fill_color),
                                        minor_tick_line_color = str(time_scat2.glyph.fill_color),
                                        axis_label= "l1015asop"), "left") 
                
        #Create marginal histogram for y-axis data density
        #set up figure
                #static total selection displayed as outline
        hist_plot = figure(plot_height = 400, plot_width = 200, y_range = time_plot.y_range)
        
        #Customize hist_plot grid lines
        hist_plot.xgrid.grid_line_alpha = 0.2
        hist_plot.ygrid.grid_line_alpha = 0.5
                
        #get histogram data 
        hist, edges = histogram(data_source.data["y1"], density = True, bins = 20)
        
        #contruct histogram
        hist_plot.quad(top=edges[1:], bottom = edges[:-1], left = 0, right = hist,
                       fill_color = "white", alpha = 0.3)
        #styleing histograms axises              
        hist_plot.xaxis.axis_label = ""
        hist_plot.yaxis.axis_label = ""
        hist_plot.xaxis.visible = None
                    
        #add gaussian kernel density estomator
        y_span = linspace(min(data_source.data["y1"]),
                             max(data_source.data["y1"]), size(data_source.data["y1"]))
        kde = gkde(data_source.data["y1"]).evaluate(y_span)
        
        #construct gaussian kernel density estomator lines    
        hist_plot.line(kde, y_span, line_color = "#ff6666", line_width = 1, alpha = 0.5)
            
        #Create updateable plots
        u_hist_source = ColumnDataSource(data=dict(top=edges[1:],bottom=edges[:-1],left=zeros_like(edges),right=hist))
        u_kde_source = ColumnDataSource(data=dict(x = kde, y = y_span))
        scat_data = ColumnDataSource(data=dict(x=[0],y=[0]))

        #Updateble histogram
        hist_plot.quad(top = 'top', bottom = 'bottom', left = 'left', right = 'right', source = u_hist_source,
                                fill_color = time_scat.glyph.fill_color, alpha = 0.5)
        #Updateble kde line
        hist_plot.line('x', 'y', source=u_kde_source ,line_color = "red")
        
        #Updateble scatter plot
        scat_plot = figure(plot_height = 400, plot_width = 400, title = "", x_axis_label = 'l1013aspv', 
                    y_axis_label = 'l1013aspv')
        #scatter plot axis cutomization
        scat_plot.yaxis.axis_line_color = time_scat.glyph.fill_color
        scat_plot.yaxis.minor_tick_line_color = time_scat.glyph.fill_color
        scat_plot.yaxis.major_tick_line_color = time_scat.glyph.fill_color
        scat_plot.yaxis.axis_label_text_color = time_scat.glyph.fill_color
        scat_plot.yaxis.major_label_text_color = time_scat.glyph.fill_color
        
        scat_plot.xaxis.axis_line_color = time_scat2.glyph.fill_color
        scat_plot.xaxis.minor_tick_line_color = time_scat2.glyph.fill_color
        scat_plot.xaxis.major_tick_line_color = time_scat2.glyph.fill_color
        scat_plot.xaxis.axis_label_text_color = time_scat2.glyph.fill_color
        scat_plot.xaxis.major_label_text_color = time_scat2.glyph.fill_color
        
        scat_plot.scatter('x', 'y', source=scat_data,size=2)
            
        data_source.callback = CustomJS(args=dict(hist_data=u_hist_source,
                                        kde_d = u_kde_source, sc=scat_data),
                                code="""
                            Update_ALL_Figures(cb_obj, hist_data, kde_d, sc)
                                    """)          
        #create plot layout
        layout = gridplot([[time_plot, hist_plot], [scat_plot, None]])
        return layout #need to return the layout
        
    # Calling plotting Function
    p = make_figure()
          
    # Extracting HTML elements
    script, div = components(p)
    
    return render_template("plot.html", script=script, div=div)