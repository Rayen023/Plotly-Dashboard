import dash
from dash import html, dcc, Input, Output, State, dash_table
import pandas as pd
import plotly.express as px
import pymongo
from bson.objectid import ObjectId
from app import collection, df

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H1('Web Application connected to a Live Database', style={'textAlign': 'center'}),
    # interval activated once/week or when page refreshed
    dcc.Interval(id='interval_db', interval=86400000 * 7, n_intervals=0),
    html.Div(id='mongo-datatable', children=[]),

    html.Div([
        html.Div(id='pie-graph', className='five columns'),
        html.Div(id='hist-graph', className='six columns'),
    ], className='row'),
    dcc.Store(id='changed-cell')
])


# Display Datatable with data from Mongo database
@app.callback(Output('mongo-datatable', component_property='children'),
              Input('interval_db', component_property='n_intervals')
              )
def populate_datatable(n_intervals):
    # Convert the Collection (table) date to a pandas DataFrame
    #df = pd.DataFrame(list(collection.find()))
    # Convert id from ObjectId to string so it can be read by DataTable
    df['_id'] = df['_id'].astype(str)
    print(df.head(20))

    return [
        dash_table.DataTable(
            id='our-table',
            data=df.to_dict('records'),
            columns=[{'id': p, 'name': p, 'editable': False} if p == '_id'
                     else {'id': p, 'name': p, 'editable': True}
                     for p in df],
            page_size=8,
        ),
    ]

# store the row id and column id of the cell that was updated
app.clientside_callback(
    """
    function (input,oldinput) {
        if (oldinput != null) {
            if(JSON.stringify(input) != JSON.stringify(oldinput)) {
                for (i in Object.keys(input)) {
                    newArray = Object.values(input[i])
                    oldArray = Object.values(oldinput[i])
                    if (JSON.stringify(newArray) != JSON.stringify(oldArray)) {
                        entNew = Object.entries(input[i])
                        entOld = Object.entries(oldinput[i])
                        for (const j in entNew) {
                            if (entNew[j][1] != entOld[j][1]) {
                                changeRef = [i, entNew[j][0]] 
                                break        
                            }
                        }
                    }
                }
            }
            return changeRef
        }
    }    
    """,
    Output('changed-cell', 'data'), #cc
    Input('our-table', 'data'),
    State('our-table', 'data_previous')
)




# Update MongoDB and create the graphs
@app.callback(
    Output("pie-graph", "children"),
    Output("hist-graph", "children"),
    Input("changed-cell", "data"),
    Input("our-table", "data"),
)
def update_d(cc, tabledata):
    if cc is None:
        # Build the Plots
        pie_fig = px.pie(tabledata, values='Salary', names='Title')
        hist_fig = px.bar(tabledata, x='Title', y='Location')
        #hist_fig = px.histogram(tabledata, x='Title', y='Location')
    else:
        print(f'changed cell: {cc}')
        print(f'Current DataTable: {tabledata}')
        x = int(cc[0])

        # update the external MongoDB
        row_id = tabledata[x]['_id']
        col_id = cc[1]
        new_cell_data = tabledata[x][col_id]
        collection.update_one({'_id': ObjectId(row_id)},
                              {"$set": {col_id: new_cell_data}})
        # Operations guide - https://docs.mongodb.com/manual/crud/#update-operations

        pie_fig = px.pie(tabledata, values='Title', names='day')
        hist_fig = px.histogram(tabledata, x='Title', y='Salary')

    return dcc.Graph(figure=pie_fig), dcc.Graph(figure=hist_fig)
    

#only runs if this file is run
if __name__ == '__main__':
    app.run_server(debug=True)
