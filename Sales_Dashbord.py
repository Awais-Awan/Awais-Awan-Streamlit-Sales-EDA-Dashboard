import streamlit as st
import pandas as pd
import plotly.express as px
import os
import warnings
import plotly.figure_factory as ff

warnings.filterwarnings('ignore')

# Streamlit page configuration
st.set_page_config(page_title='Superstore!!!', page_icon=':bar_chart:', layout='wide')
st.title(':bar_chart: Sample SuperStore EDA')
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

# File uploader
fl = st.file_uploader(':file_folder: Upload a file', type=['csv', 'txt', 'xlsx', 'xls'])

# Load file based on its extension
if fl is not None:
    filename = fl.name
    st.write(f"Filename: {filename}")
    try:
        if filename.endswith(('.xls', '.xlsx')):
            # Read Excel files
            df = pd.read_excel(fl)
        elif filename.endswith(('.csv', '.txt')):
            # Read CSV or TXT files with specific handling for bad lines
            df = pd.read_csv(fl, encoding='ISO-8859-1', on_bad_lines='skip')
        else:
            st.error("Unsupported file type!")
            df = None

        # Display the first few rows of the dataset
        if df is not None:
            pass
            # st.write("Preview of the dataset:")
            # st.write(df.head())

    except Exception as e:
        st.error(f"Error loading file: {e}")
else:
    try:
        # Fallback to a default file path if no file is uploaded
        os.chdir(r'D:/Python/Data Analytics/05. EDA-with-python-on-streamlit')
        df = pd.read_excel(r'Superstore.xls')
        # st.write("Loaded default Superstore.xls")
        # st.write(df.head())
    except Exception as e:
        st.error(f"Error loading default file: {e}")

col1,col2=st.columns((2))
df['Order Date']=pd.to_datetime(df["Order Date"])

startDate=pd.to_datetime(df["Order Date"]).min()
endDate=pd.to_datetime(df["Order Date"]).max()

with col1:
    date1=pd.to_datetime(st.date_input("Start Date",startDate))

with col2:
    date2=pd.to_datetime(st.date_input("End Date",endDate))


df=df[(df['Order Date']>=date1)&(df['Order Date']<=date2)].copy()
# st.write("Loaded default Superstore.xls")
# st.write(df.head())

region=st.sidebar.multiselect("Pick your Region", df['Region'].unique())
if not region:
    df2=df.copy()
else:
    df2=df[(df["Region"].isin(region))]

states=st.sidebar.multiselect("Pick your State", df2['State'].unique())
if not states:
    df3=df2.copy()
else:
    df3=df2[(df2["State"].isin(states))]
    


city= st.sidebar.multiselect("Pick the city",df3['City'].unique())

if not region and not states and not city:
    filtered_df=df
elif not states and not city:
    filtered_df=df[(df['Region'].isin(region))]
elif not region and not city:
    filtered_df=df[(df['State'].isin(states))]
elif states and city:
    filtered_df=df[(df['State'].isin(states) & df3["City"].isin(city))]
elif region and city:
    filtered_df= df3[(df['State'].isin(region) & df3["City"].isin(city))]
elif region and states:
    filtered_df= df3[(df['State'].isin(region) & df3["City"].isin(states))]
elif city:
    filtered_df=df3[df['City'].isin(city)]
else:
    filtered_df= df3[df3['Region'].isin(region) & df3['State'].isin(states) & df3['City'].isin(city)]
    



category_df=filtered_df.groupby('Category',as_index=False)['Sales'].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df,x='Category',y='Sales', text=['${:,.2f}'.format(x) for x in category_df['Sales']]
                 ,template='seaborn')
    
    st.plotly_chart(fig,use_container_width=True,height=200)
    
    
with col2:
    st.subheader("Region wise Sales")
    fig=px.pie(filtered_df,values="Sales",names="Region",hole=0.5)
    fig.update_traces(text=filtered_df["Region"],textposition='outside')
    st.plotly_chart(fig,use_container_width=True)
    
    
cl1, cl2 =st.columns(2)

with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv=category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data",data=csv,file_name="Category.csv",mime="text/csv",
                           help="Click here to download the data as CSV file")

with cl2:
    with st.expander("Region_ViewData"):
        region=filtered_df.groupby("Region",as_index=False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv=region.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data",data=csv,file_name="Region.csv",mime="text/csv",
                            help="Click here to download the data as CSV file")



filtered_df['month_year']=filtered_df['Order Date'].dt.to_period("M")
st.subheader("Time Series Analysis")

linechart_df=pd.DataFrame(filtered_df.groupby(filtered_df['month_year'].dt.strftime('%Y : %b'))['Sales'].sum()).reset_index()
fig2=px.line(linechart_df,x='month_year',y='Sales',
             labels={'Sales':'Amount'},height=500,width=1000,template='gridon')
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of Time Series"):
    st.write(linechart_df.T.style.background_gradient(cmap='Blues'))
    csv=linechart_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data",data=csv,file_name='Timeseries.csv',mime='text/csv')
    


st.subheader("Hierarchical view of Sales using TreeMap")
fig3=px.treemap(filtered_df,path=['Region','Category','Sub-Category'],values='Sales',hover_data=['Sales'],
                color='Sub-Category')

fig3.update_layout(width=800,height=650)
st.plotly_chart(fig3,use_container_width=True)


chart1, chart2=st.columns(2)
with chart1:
    st.subheader('Segment wise Sales')
    fig=px.pie(filtered_df,values="Sales",names="Segment",template='plotly_dark')
    fig.update_traces(text=filtered_df['Segment'], textposition='inside')
    st.plotly_chart(fig,use_container_width=True)
    
with chart2:
    st.subheader('Category wise Sales')
    fig=px.pie(filtered_df,values="Sales",names="Category",template='gridon')
    fig.update_traces(text=filtered_df['Category'], textposition='inside')
    st.plotly_chart(fig,use_container_width=True)
    

st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample=df[0:5][["Region","State","City","Category","Sales","Profit","Quantity"]]
    fig=ff.create_table(df_sample,colorscale="blues",)
    st.plotly_chart(fig,use_container_width=True)
    
    st.markdown("Month wise sub-category table")
    filtered_df['Month']=filtered_df['Order Date'].dt.month_name()
    sub_category_year=pd.pivot_table(data=filtered_df,values="Sales",index=["Sub-Category"],columns="Month")
    st.write(sub_category_year.style.background_gradient(cmap='Blues'))
    
    
    
data1=px.scatter(filtered_df,x="Sales", y="Profit", size="Quantity")
data1['layout'].update(title="Relationship Between Sales And Profits Using Scatter Plot.",
                       titlefont=dict(size=20),xaxis=dict(title="Sales",titlefont=dict(size=19)),
                       yaxis=dict(title="Profit",titlefont=dict(size=19)))

st.plotly_chart(data1,use_container_width=True)



with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Blues"))
    
csv=df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name="Data.csv",mime='text/csv')
