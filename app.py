import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import pandas as pd

tweet_data = pd.read_csv('ProcessedTweets.csv')

app = dash.Dash(__name__)

app.layout = html.Div(className='parent', children=[
    html.Div(className='row1', children=[
        html.Div(className='row1_1', children=[
            html.P('Month'),
            dcc.Dropdown(
                id='month-dropdown',
                options=tweet_data.Month.unique(),
                value=tweet_data.Month.unique()[0],
                style={'width': '150px'}) 
        ]),
        html.Div(className='row1_2', children=[
            html.P('Sentiment Score'),
            html.Div(
                dcc.RangeSlider(
                    id='sentiment-slider',
                    value=[-1,1],
                    marks={-1: '-1', 1: '1'},
                    min=tweet_data.Sentiment.min(),
                    max=tweet_data.Sentiment.max(),
                    allowCross=False),
                style={'width':'150px'})
        ]),
        html.Div(className='row1_3', children=[
            html.P('Subjectivity Score'),
            html.Div(
                dcc.RangeSlider(
                    id='subj-slider',
                    value=[0,1],
                    marks={0: '0', 1: '1'},
                    min=tweet_data.Subjectivity.min(),
                    max=tweet_data.Subjectivity.max(),
                    allowCross=False),
                style={'width':'150px'})             
        ])
    ]),
    html.Div(className='row2', children=[
        dcc.Graph(id='scatterplot')
    ]),
    html.Div(className='row3', children=[
        dash_table.DataTable(
            id='tweet-table',
            columns=[{'name': 'RawTweet', 'id': 'RawTweet'}],
            data=[],
            style_cell={'textAlign': 'center',
                        'whiteSpace': 'pre-line',
                        'overflowWrap': 'break-word'},
            style_table={'overflowY': 'auto'},
            page_size=10
        )
    ])
])

# Callback for updating the scatterplot
@app.callback(Output('scatterplot', 'figure'),
              [Input('month-dropdown', 'value'),
               Input('sentiment-slider', 'value'),
               Input('subj-slider', 'value')])
def update_figure(month, sent, subj):
    filtered_df = tweet_data[tweet_data['Month'] == month][(tweet_data['Sentiment'] >= sent[0]) & (tweet_data['Sentiment'] <= sent[1])][(tweet_data['Subjectivity'] >= subj[0]) & (tweet_data['Subjectivity'] <= subj[1])]
    fig = px.scatter(filtered_df, 'Dimension 1', 'Dimension 2', color_discrete_sequence=['gray'], opacity=0.7)
    fig.update_xaxes(range=[-50, 50])
    fig.update_yaxes(range=[-45, 55])
    fig.update_traces(marker={'size': 10})
    fig.update_layout(
        xaxis_title='',
        yaxis_title='',
        xaxis=dict(showticklabels=False, showline=False),
        yaxis=dict(showticklabels=False)
    )
    return fig

# Callback for updating the table
@app.callback(Output('tweet-table', 'data'),
              [Input('scatterplot', 'selectedData')])
def update_table(selectedData):
    if selectedData is not None:
        indices = [point['pointIndex'] for point in selectedData['points']]
        raw_tweets = tweet_data[['RawTweet']]
        selected_df = raw_tweets.iloc[indices]
        return selected_df.to_dict('records')
    return []

# For local
if __name__ == '__main__':
    app.run_server(debug=True)

# For AWS
# if __name__ == '__main__':
#     app.run_server(host='0.0.0.0', debug=False)