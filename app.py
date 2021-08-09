import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

%%capture
gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown_text = '''
The [General Social Survey] (http://www.gss.norc.org/About-The-GSS) (GSS) is a national survey conducted across the USA since 1972 focusing on data collection to enhance our understanding of opinions as they manifest into behaviors. To support our understanding of the survey, the following dashboard has been developed which focused on key issues surrounding the gender wage gap domestically. 

According to the [US Department of Labor] (https://blog.dol.gov/2021/03/19/5-facts-about-the-state-of-the-gender-pay-gap), women earn 82 cents for every dollar earned by men (other reports have it closer to 84). This issue extrapolates beyond women’s working years as well, impacting their benefits such as Social Security during retirement given that less earnings earlier in life equates to lower benefits upon retirement. Although progress has been made in comparison to the 70’s when the GSS survey started (women were at 57 cents for every dollar earned by men), events such as the pandemic have stalled the progress toward equality. When factoring race and holding all else equal (i.e. education and years of experience), the gap widens further to 65% for Black and Latina women.

As noted by [Pew Research Center] (https://www.pewresearch.org/fact-tank/2021/05/25/gender-pay-gap-facts/), this wage gap of 16-18 cents in median earnings equates to an additional ~42 days of work annually for women in order to be equal to men. The age gap is improving when factoring in age as for women 25-35, a gap of 93 cents exists showing progress through generations. Similar PEW Research has identified 40% of women experienced gender discrimination, a hypothesized key contributor to the ongoing issue.

'''

#create table display
gss_clean_display = gss_clean.groupby('sex').agg({'income' : 'mean',
                                        'job_prestige' : 'mean',
                                                 'socioeconomic_index' : 'mean',
                                                 'education' : 'mean'})

#rename table attributes
gss_clean_display = gss_clean_display.rename({'income':'Avg. Income',
                                   'job_prestige':'Avg. Job Prestige',
                                   'socioeconomic_index':'Avg. Socioeconomic Index',
                                   'education':'Avg. Years of Education'}, axis=1)

#round all results 2 decimal places
gss_clean_display = round(gss_clean_display, 2)

#reset index and rename 'sex' to 'gender'
gss_clean_display = gss_clean_display.reset_index().rename({'sex':'Gender'}, axis=1)


#format table in interactive, web-enabled form
table = ff.create_table(gss_clean_display)

gss_clean_bar = gss_clean[['sex', 'male_breadwinner']]
gss_clean_bar['count'] = 1
gss_clean_bar = gss_clean_bar.groupby(['sex', 'male_breadwinner']).agg({'count' : 'sum'})

#convert back to standard df structure
gss_clean_bar = pd.DataFrame(gss_clean_bar.to_records())

fig_bar = px.bar(gss_clean_bar, x='male_breadwinner', y='count', color='sex', 
             facet_col='sex',
             hover_data = ['male_breadwinner', 'count', 'sex'],
            labels={'male_breadwinner':'Male Breadwinner Categories', 'sex':'Gender', 'count' : '# of Responses'},
            text='sex')
fig_bar.update(layout=dict(title=dict(x=0.5)))
fig_bar.update_layout(showlegend=False)
fig_bar.for_each_annotation(lambda a: a.update(text=a.text.replace("sex=", "")))

fig_scat = px.scatter(gss_clean, x='job_prestige', y='income', 
                 trendline='ols', color = 'sex', 
                 height=600, width=600,
                 labels={'job_prestige':'Occupational Job Prestige Score', 
                        'income':'Annual Income ($)',
                        'sex' : 'Gender'},
                 hover_data=['job_prestige', 'income', 'sex', 'education', 'socioeconomic_index'])
fig_scat.update(layout=dict(title=dict(x=0.5)))

fig_box1 = px.box(gss_clean, x='sex', y = 'income', color = 'sex',
                   labels={'income':'Annual Income ($)'})
fig_box1.update_layout(showlegend=False)
fig_box1.update(layout=dict(title=dict(x=0.5)))

fig_box2 = px.box(gss_clean, x='sex', y = 'job_prestige', color = 'sex',
                   labels={'job_prestige':'Occupational Job Prestige Score'})
fig_box2.update_layout(showlegend=False)
fig_box2.update(layout=dict(title=dict(x=0.5)))

#create new df with job prestige bins
gss_clean_df = gss_clean[['income', 'sex', 'job_prestige']]
gss_clean_df['jp_cat'] = pd.cut(gss_clean_df.job_prestige, 
                                bins = [15.9, 26.9, 37.9, 48.9, 59.9, 70.9, 82.9], 
                                labels = ("Very Low", "Low", "Medium", "High", "Very High", "Premium"))

#reorder categories in desired order
gss_clean_df['jp_cat'] = gss_clean_df['jp_cat'].cat.reorder_categories(["Very Low", "Low", "Medium", "High", "Very High", "Premium"])

#drop rows with missing values
gss_clean_df.dropna(inplace=True)

fig_box_6 = px.box(gss_clean_df, x='sex', y='job_prestige', facet_col='jp_cat', facet_col_wrap=2, color = 'sex',
                   labels={'sex':'Gender', 'job_prestige':'Occupational Job Prestige Score', 'jp_cat' : 'Job Prestige Category'},
            width=1000, height=1000)
fig_box_6.update(layout=dict(title=dict(x=0.5)))
fig_box_6.update_layout(showlegend=False)

app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div(
    [
        html.H1("Exploring the General Social Survey Results"),
        
        dcc.Markdown(children = markdown_text),
        
        html.H2("Avg. Indicators for Men vs. Women Influencing Wage Gap"),
        
        dcc.Graph(figure = table),      
        
        html.H2("Male Breadwinner Categories by Gender"),
        
        dcc.Graph(figure = fig_bar),
        
        html.H2("Annual Income ($) vs Occupational Job Prestige Score by Gender"),
        
        dcc.Graph(figure = fig_scat),
        
        html.Div([
            html.H2("Annual Income ($) by Gender"),
            
            dcc.Graph(figure = fig_box1)
            
        ], style = {'width' : '48%', 'float' : 'left'}),
        
        html.Div([
            html.H2("Occupational Job Prestige Score by Gender"),
            
            dcc.Graph(figure = fig_box2)
        ], style = {'width' : '48%', 'float' : 'right'}),
        
        html.H2("Occupational Job Prestige Score & Category by Gender"),
        
        dcc.Graph(figure = fig_box_6)
        
    ]
)



if __name__ == '__main__':
    app.run_server(mode = 'inline', debug=True, port = 8053)
