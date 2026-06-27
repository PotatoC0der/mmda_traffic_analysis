import pandas as pd
import re

df = pd.read_csv('data_mmda_traffic_spatial.csv')

df = df.drop(columns=["Tweet","Source"]) # dropping the unnecessary columns
df = df[df['High_Accuracy'] == 1].drop(columns=['High_Accuracy']) # dropping low accuracy entries
df = df.dropna(subset=['Time', 'City']) # dropping null rows as time and city are needed in my data exploration

df['Month'] = pd.to_datetime(df['Date']).dt.strftime('%B %Y')  # added a column only retaining year and month

df['Time_parsed'] = pd.to_datetime(df['Time'], format='%I:%M %p', errors='coerce')
df['Hour'] = df['Time_parsed'].dt.hour.astype('Int64')  # added a column with the time in hours only
df = df.drop(columns=['Time_parsed']) # dropped column as hour is already extracted

df['City'] = df['City'].str.replace('ParaÃ±aque', 'Parañaque', regex=False) # fixing data entry
df['City'] = df['City'].str.replace(' City', '', regex=False) # making values consistent

valid_dirs = ['NB', 'SB', 'EB', 'WB']
df['Direction'] = df['Direction'].where(df['Direction'].isin(valid_dirs), other=None) # removing unnecessary data

df['Lanes_Blocked'] = df['Lanes_Blocked'].astype('Int64') # changing data type to int

# dealing with nulls
df['Lanes_Blocked'] = df['Lanes_Blocked'].fillna(1).astype('Int64')
df['Direction'] = df['Direction'].fillna('Unknown')
df['Involved'] = df['Involved'].fillna('Unknown')

# ONLY run code below to check for nulls
# df.isnull().sum()

# adding a new clean "type" column
def categorize_type(val):
    if pd.isna(val):
        return None
    v = str(val).upper().strip()

    if re.search(
            r'VEH[A-Z]*\s*ACCIDENT|VEHICULAR ACIDENT|VEHICULAR ACCIEDNT|VEHICULAR ACCCIDENT|VEHCICULAR|VEHICHULAR|VEHICULAR|VEHICUKAR|VEHICUALR|VEHICUKLAR',
            v):
        return 'Vehicular Accident'
    if re.search(r'MUL[A-Z]*\s*COL+ISION|MULTIPLE COLL', v):
        return 'Multiple Collision'
    if v.startswith('SELF ACCIDENT') or 'SELF ACCIDENT' in v:
        return 'Self Accident'
    if re.search(r'VEHIC[A-Z]* (ON )?FIRE|VEHICLE ON FIRE', v):
        return 'Vehicular Fire'
    if v.startswith('STALLED') or 'STALLED' in v:
        return 'Stalled Vehicle'
    if re.search(
            r'DPWH|MAYNILAD|MERALCO|MMDA TEC|ROAD PATCH|REBLOCKING|RE-BLOCKING|RE BLOCKING|DECLOGGING|ROAD REPAIR|ASPHAL|LANE MARK|MANHOLE REPAIR|FLOOD CONTROL|DRAINAGE REPAIR|CEMENT POUR|SQUARING|ROAD REHAB|BEAUTIFICATION|TARPAULIN|WALL CLEAN|WALL PAINT|BARRIER MAINT|FOOTBRIDGE|MMDA MPCG|ONGOING.*REPAIR|ONGOING.*ROAD',
            v): # this has to be the most tiring clean of my life T-T
        return 'Road Works'
    if re.search(r'ROAD CLOSURE|TEMPORARY.*CLOSURE', v):
        return 'Road Closure'
    if re.search(r'RALLY|MOTORCADE|PARADE|CARAVAN|MARCH|PROCESSION|MOTORCAMP', v):
        return 'Public Event'
    if re.search(r'SHOOTING|STABBING|HIT AND RUN|SUSPICIOUS|DEAD PERSON', v):
        return 'Incident'
    if re.search(
            r'OIL SPILL|FALLEN TREE|TREE HAS FALLEN|OPEN MANHOLE|DRAINAGE HOLE|MISALIGNED|FALLEN WALL|FALLEN BOARD', v):
        return 'Hazard'
    return 'Other'

df['Type_Category'] = df['Type'].apply(categorize_type)

# print(df[['Date', 'Month']].head(10).to_string())
print(df.loc[0:50].to_string())