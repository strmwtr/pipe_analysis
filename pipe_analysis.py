import arcpy 
import os

#Setup workspace and environments
arcpy.env.workspace = r'C:\Users\brownr\Desktop\Pipe_Network.gdb'
gdb = r'C:\Users\brownr\Desktop\Pipe_Network.gdb'


def initialize():
    #Delete everything in gdb except for Basins, Neighborhoods, and Pipes
    tables = arcpy.ListTables()
    feats = arcpy.ListFeatureClasses()
    for feat in feats:
        if feat not in ("Basins", "Neighborhoods", "Pipes"):
            arcpy.Delete_management(feat)
    for table in tables:
        arcpy.Delete_management(table)

    print "Done initialize"

def copy_basins():
    #Take each basin from Basins and make new feature in gdb
    feats = arcpy.ListFeatureClasses()
    arcpy.MakeFeatureLayer_management("Basins", "lyr")

    for x in arcpy.da.SearchCursor("lyr", "NAME"):
        feat = str(x)[3:-3]

        if ' ' and '\'' in feat:
            nospace = feat.replace(' ','')
            out_name = nospace.replace('\'','')
        elif ' ' in feat:
            out_name = feat.replace(' ','')
        else:
            out_name = feat

        if '\'' in feat:
            rep = feat.index('\'')
            fix_feat = feat[:rep] + '\'' + feat[rep:]

            arcpy.SelectLayerByAttribute_management("lyr", 
            "NEW_SELECTION","NAME = \'{0}\'".format(fix_feat))
            arcpy.FeatureClassToFeatureClass_conversion('lyr',gdb,
            'B_{0}'.format(out_name))
        else:         
            arcpy.SelectLayerByAttribute_management("lyr", 
            "NEW_SELECTION","NAME = \'{0}\'".format(feat))
            arcpy.FeatureClassToFeatureClass_conversion('lyr',gdb,
            'B_{0}'.format(out_name))
    arcpy.Delete_management("lyr")

    print 'Done copy_basins'

def copy_nbhs():
    #Take each neighborhood from Neighborhoods and make new feature in gdb
    feats = arcpy.ListFeatureClasses()
    arcpy.MakeFeatureLayer_management("Neighborhoods", "lyr")

    for x in arcpy.da.SearchCursor("lyr", "NAME"):
        feat = str(x)[3:-3]

        if ' ' and '\'' in feat:
            nospace = feat.replace(' ','')
            out_name = nospace.replace('\'','')
        elif ' ' in feat:
            out_name = feat.replace(' ','')
        else:
            out_name = feat

        if '\'' in feat:
            rep = feat.index('\'')
            fix_feat = feat[:rep] + '\'' + feat[rep:]

            arcpy.SelectLayerByAttribute_management("lyr", 
            "NEW_SELECTION","NAME = \'{0}\'".format(fix_feat))
            arcpy.FeatureClassToFeatureClass_conversion('lyr',gdb,
            'N_{0}'.format(out_name))
        else:         
            arcpy.SelectLayerByAttribute_management("lyr", 
            "NEW_SELECTION","NAME = \'{0}\'".format(feat))
            arcpy.FeatureClassToFeatureClass_conversion('lyr',gdb,
            'N_{0}'.format(out_name))
    arcpy.Delete_management("lyr")

    print 'Done copy_nbhs'

def clip_pipes():
    #Clip pipe layer by Basins and Neighborhoods
    feats = arcpy.ListFeatureClasses()
    for feat in feats:
        if feat.startswith("B_") and not feat.endswith("_P"):
            arcpy.Clip_analysis("Pipes", feat, "{0}_P".format(feat))
            arcpy.SpatialJoin_analysis("{0}_P".format(feat), feat, 
            "{0}_SJ_P".format(feat), 
            match_option="INTERSECT")
            arcpy.Delete_management("{0}_P".format(feat))
        elif feat.startswith("N_") and not feat.endswith("_P"):
            arcpy.Clip_analysis("Pipes", feat, "{0}_P".format(feat))
            arcpy.SpatialJoin_analysis("{0}_P".format(feat), 
            feat, "{0}_SJ_P".format(feat), match_option="INTERSECT")
            arcpy.Delete_management("{0}_P".format(feat))

    print "Done clip_pipes"

def stats():
    #Create stats tables for length and count of items in gdb ending in _Pipes
    feats = arcpy.ListFeatureClasses()
    for feat in feats:
        if feat.endswith('SJ_P'):
            arcpy.Statistics_analysis(feat, "{0}\\{1}_T_S".format(gdb,feat),
            [['SHAPE_Length','SUM']], 'TYPE')
            arcpy.Statistics_analysis(feat, "{0}\\{1}_O_S".format(gdb,feat),
            [['SHAPE_Length','SUM']], 'PRIVATE_LINE')
            arcpy.Statistics_analysis(feat, "{0}\\{1}_R_S".format(gdb,feat),
            [['SHAPE_Length','SUM']], 'Rehabilitated')
            arcpy.Statistics_analysis(feat, "{0}\\{1}_A_S".format(gdb,feat),
            [['acres','MEAN']])

    print "Done stats"

def add_field_stats():
    tables = arcpy.ListTables()
    for table in tables:
        if table.endswith("_S"):
            arcpy.AddField_management(table, "NAME", "TEXT", field_length = 40)

    print "Done add_field_stats"

def name_stats():
    #Populate NAME field in stats table with Basin or NBH
    tables = arcpy.ListTables()
    for table in tables:
        if table.endswith("_S"):
            name = str(table.split("_")[0] +"_"+ table.split("_")[1])
            arcpy.CalculateField_management(table, 
            "NAME", "'{0}'".format(name), 'PYTHON_9.3')

    print "Done name_stats"

def merge():
    #Merges all tables in gdb to create StatsMerge
    tables = arcpy.ListTables()
    arcpy.Merge_management(tables,"{0}\\StatsMerge".format(gdb))

    print "Done merge"

def post_stats():
    #Delete all items in gdb except StatsMerge, Bains, Pipes, and Neighborhoods
    tables = arcpy.ListTables()
    feats = arcpy.ListFeatureClasses()

    for table in tables:
        if table != "StatsMerge":
            arcpy.Delete_management(table)
    for feat in feats:
        if feat not in ("Basins", "Neighborhoods", "Pipes"):
            arcpy.Delete_management(feat)

    print "Done post_stats"

def add_fields():
    #Add fields to StatsMerge to hold values 
    #Acres
    arcpy.AddField_management('StatsMerge', "Acres", "FLOAT")
    #Private Pipe Length
    arcpy.AddField_management('StatsMerge', "Private_Length", "FLOAT")
    #Private Pipe Count
    arcpy.AddField_management('StatsMerge', "Private_Count", "FLOAT")
    #Public Pipe Length
    arcpy.AddField_management('StatsMerge', "Public_Length", "FLOAT")
    #Public Pipe Count
    arcpy.AddField_management('StatsMerge', "Public_Count", "FLOAT")
    #Rehab Pipe Length
    arcpy.AddField_management('StatsMerge', "Rehab_Length", "FLOAT")
    #Rehab Pipe Count
    arcpy.AddField_management('StatsMerge', "Rehab_Count", "FLOAT")
    #RCP Pipe Length
    arcpy.AddField_management('StatsMerge', "RCP_Length", "FLOAT")
    #RCP Pipe Count
    arcpy.AddField_management('StatsMerge', "RCP_Count", "FLOAT")
    #VC Pipe Length
    arcpy.AddField_management('StatsMerge', "VC_Length", "FLOAT")
    #VC Pipe Count
    arcpy.AddField_management('StatsMerge', "VC_Count", "FLOAT")
    #CMP Pipe Length
    arcpy.AddField_management('StatsMerge', "CMP_Length", "FLOAT")
    #CMP Pipe Count
    arcpy.AddField_management('StatsMerge', "CMP_Count", "FLOAT")
    #PVC Pipe Length
    arcpy.AddField_management('StatsMerge', "PVC_Length", "FLOAT")
    #PVC Pipe Count
    arcpy.AddField_management('StatsMerge', "PVC_Count", "FLOAT")
    #HDPE Pipe Length
    arcpy.AddField_management('StatsMerge', "HDPE_Length", "FLOAT")
    #HDPE Pipe Count
    arcpy.AddField_management('StatsMerge', "HDPE_Count", "FLOAT")
    #OTHER Pipe Length
    arcpy.AddField_management('StatsMerge', "Other_Length", "FLOAT")
    #OTHER Pipe Count
    arcpy.AddField_management('StatsMerge', "Other_Count", "FLOAT")
    #DIP Pipe Length
    arcpy.AddField_management('StatsMerge', "DIP_Length", "FLOAT")
    #DIP Pipe Count
    arcpy.AddField_management('StatsMerge', "DIP_Count", "FLOAT")

    print "Done add_fields"

def pop_fields():
    #Populates fields created in add_fields
    #Acres
    cursor = arcpy.da.UpdateCursor('StatsMerge',['MEAN_acres', 'Acres'])
    for row in cursor:
        row[1] = row[0]
        cursor.updateRow(row)
    #Private Pipe Length
    cursor = arcpy.da.UpdateCursor('StatsMerge',['PRIVATE_LINE', 
    'SUM_SHAPE_Length', 'Private_Length'], "PRIVATE_LINE = \'Yes\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #Private Pipe Count
    cursor = arcpy.da.UpdateCursor('StatsMerge',['PRIVATE_LINE', 
    'FREQUENCY', 'Private_Count'], "PRIVATE_LINE = \'Yes\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #Public Pipe Length
    cursor = arcpy.da.UpdateCursor('StatsMerge',['PRIVATE_LINE', 
    'SUM_SHAPE_Length', 'Public_Length'], "PRIVATE_LINE = \'No\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #Public Pipe Count
    cursor = arcpy.da.UpdateCursor('StatsMerge',['PRIVATE_LINE', 
    'FREQUENCY', 'Public_Count'], "PRIVATE_LINE = \'No\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #Rehab Pipe Length
    cursor = arcpy.da.UpdateCursor('StatsMerge',['REHABILITATED', 
    'SUM_SHAPE_Length', 'Rehab_Length'], "REHABILITATED = \'Y\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #Rehab Pipe Count
    cursor = arcpy.da.UpdateCursor('StatsMerge',['REHABILITATED', 
    'FREQUENCY', 'Rehab_Count'], "REHABILITATED = \'Y\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #RCP Pipe Length
    cursor = arcpy.da.UpdateCursor('StatsMerge',['TYPE', 'SUM_SHAPE_Length', 
    'RCP_Length'], "TYPE = \'RCP\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #RCP Pipe Count
    cursor = arcpy.da.UpdateCursor('StatsMerge',['TYPE', 'FREQUENCY', 
    'RCP_Count'], "TYPE = \'RCP\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #VC Pipe Length
    cursor = arcpy.da.UpdateCursor('StatsMerge',['TYPE', 'SUM_SHAPE_Length', 
    'VC_Length'], "TYPE = \'VC\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #VC Pipe Count
    cursor = arcpy.da.UpdateCursor('StatsMerge',['TYPE', 'FREQUENCY', 
    'VC_Count'], "TYPE = \'VC\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #CMP Pipe Length
    cursor = arcpy.da.UpdateCursor('StatsMerge',['TYPE', 'SUM_SHAPE_Length', 
    'CMP_Length'], "TYPE = \'CMP\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #CMP Pipe Count
    cursor = arcpy.da.UpdateCursor('StatsMerge',['TYPE', 'FREQUENCY', 
    'CMP_Count'], "TYPE = \'CMP\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #PVC Pipe Length
    cursor = arcpy.da.UpdateCursor('StatsMerge',['TYPE', 'SUM_SHAPE_Length', 
    'PVC_Length'], "TYPE = \'PVC\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #PVC Pipe Count
    cursor = arcpy.da.UpdateCursor('StatsMerge',['TYPE', 'FREQUENCY', 
    'PVC_Count'], "TYPE = \'PVC\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #HDPE Pipe Length
    cursor = arcpy.da.UpdateCursor('StatsMerge',['TYPE', 'SUM_SHAPE_Length', 
    'HDPE_Length'], "TYPE = \'HDPE\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #HDPE Pipe Count
    cursor = arcpy.da.UpdateCursor('StatsMerge',['TYPE', 'FREQUENCY', 
    'HDPE_Count'], "TYPE = \'HDPE\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #OTHER Pipe Length
    cursor = arcpy.da.UpdateCursor('StatsMerge',['TYPE', 'SUM_SHAPE_Length', 
    'Other_Length'], "TYPE = \'Other\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #OTHER Pipe Count
    cursor = arcpy.da.UpdateCursor('StatsMerge',['TYPE', 'FREQUENCY', 
    'Other_Count'], "TYPE = \'Other\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #DIP Pipe Length
    cursor = arcpy.da.UpdateCursor('StatsMerge',['TYPE', 'SUM_SHAPE_Length', 
    'DIP_Length'], "TYPE = \'DIP\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)
    #DIP Pipe Count
    cursor = arcpy.da.UpdateCursor('StatsMerge',['TYPE', 'FREQUENCY', 
    'DIP_Count'], "TYPE = \'DIP\'")
    for row in cursor:
        row[2] = row[1]
        cursor.updateRow(row)

    print "Done pop_fields"

def clean_stats():
    #Deletes unneeded fields in StatsMerge
    arcpy.DeleteField_management("StatsMerge", ["SUM_SHAPE_Length", "TYPE", 
    "FREQUENCY", "PRIVATE_LINE", "REHABILITATED", "MEAN_acres"])

    print "Done clean_stats"

def get_data():
    #Compile data to single row
    compiled_table = []
    fields = []
    for field in arcpy.ListFields('StatsMerge'):
        fields.append(field.name)
    compiled_table.append(fields)
    data_table = []
    cursor = arcpy.da.UpdateCursor('StatsMerge',fields)
    for row in cursor:
        data_table.append(row)
    AOIs = []
    for x in data_table:
        if x[1] not in AOIs:
            AOIs.append(x[1])
    updated_row = [None] * 23
    counter = 0
    while counter <= len(AOIs) - 1:
        for row in data_table:
            if row[1] == AOIs[counter]:
                for x in row:
                    if x != None:
                        updated_row[row.index(x)] = x
        compiled_table.append(updated_row)
        counter = counter + 1
        updated_row = [None] * 23
    f = open(r'C:\Users\brownr\Desktop\stats.txt', 'w')
    for row in compiled_table:
        f.write('{0} \n'.format(row))
    f.close()

    print "Done get_data"

def fresh(check):
    #Checks if a file exists and deletes it. 
    #**Note that this needs to be called with variable, unlike any other 
    #function in script***
    if os.path.exists(check):
        os.remove(check)

    print "Done fresh"

def clean():
    #Creates txt files from StatsMerge and formats for easy reading 
    #Create Pipe_Stats in gdb, then deletes txt files created and StatsMerge
    txt_og = r'C:\Users\brownr\Desktop\stats.txt'
    txt_new = r'C:\Users\brownr\Desktop\stats2.txt'
    f = open(txt_og, 'r+')
    n = open(txt_new, 'w')
    content = []
    for lines in f.readlines():
        content.append(str(lines))
    f.close()
    for x in content:
        x = x.replace("u'","")
        x = x.replace("'","")
        x = x.replace("[","")
        x = x.replace("]","")
        x = x.replace(" ","")
        for y in x.split(","):
            try:
                y = round(float(y),1)
            except:
                pass
        n.write(x)
    n.close()
    arcpy.TableToTable_conversion(txt_new,gdb,"Pipe_Stats")
    fresh(txt_og)
    fresh(txt_new)
    arcpy.Delete_management("StatsMerge")

    print "Done clean"

def round_vals():
    #Rounds length values to 1 decimal place, updates
    cursor = arcpy.da.UpdateCursor('Pipe_Stats',['Acres', 'Private_Length',
    'Public_Length', 'Rehab_Length','RCP_Length','VC_Length','CMP_Length',
    'PVC_Length','HDPE_Length', 'Other_Length','DIP_Length'])
    for row in cursor:
        for x in row:
            if type(x) is unicode:
                if x == "None":
                    row[row.index(x)] = 0
                else:
                    row[row.index(x)] = round(float(x),1)
            elif x is None:
                row[row.index(x)] = 0
            else:
                row[row.index(x)] = round(x,1)
        cursor.updateRow(row)

    print "Done round_vals"

def null_zeros():
    #Changes all count values to floats, and nulls and nones will be 0's
    fields = []
    for field in arcpy.ListFields('Pipe_Stats'):
        if field.name.endswith("Count"):
            fields.append(field.name)
    cursor = arcpy.da.UpdateCursor('Pipe_Stats',fields)
    for row in cursor:
        for x in row:
            if type(x) is float:
                row[row.index(x)] = int(round(float(x),0))
            elif x is None:
                row[row.index(x)] = 0
            elif x == "None":
                row[row.index(x)] = 0
            else:
                row[row.index(x)] = int(round(float(x),0))
        cursor.updateRow(row)

    print "Done null_zeros"

def add_more_fields():
    #Adds fields to Pipe_Stats
    arcpy.AddField_management('Pipe_Stats', "Total_Length", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "Total_Count", "SHORT")    

    arcpy.AddField_management('Pipe_Stats', "Pipe_Count_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "Pipe_Length_Ac", "FLOAT")

    arcpy.AddField_management('Pipe_Stats', "Private_Count_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "Private_Length_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "Private_Count_Percent", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "Private_Length_Percent", "FLOAT")

    arcpy.AddField_management('Pipe_Stats', "Public_Count_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "Public_Length_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "Public_Count_Percent", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "Public_Length_Percent", "FLOAT")

    arcpy.AddField_management('Pipe_Stats', "Rehab_Count_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "Rehab_Length_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "Rehab_Count_Percent", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "Rehab_Length_Percent", "FLOAT")

    arcpy.AddField_management('Pipe_Stats', "RCP_Count_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "RCP_Length_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "RCP_Count_Percent", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "RCP_Length_Percent", "FLOAT")

    arcpy.AddField_management('Pipe_Stats', "VC_Count_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "VC_Length_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "VC_Count_Percent", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "VC_Length_Percent", "FLOAT")

    arcpy.AddField_management('Pipe_Stats', "CMP_Count_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "CMP_Length_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "CMP_Count_Percent", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "CMP_Length_Percent", "FLOAT")

    arcpy.AddField_management('Pipe_Stats', "PVC_Count_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "PVC_Length_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "PVC_Count_Percent", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "PVC_Length_Percent", "FLOAT")

    arcpy.AddField_management('Pipe_Stats', "HDPE_Count_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "HDPE_Length_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "HDPE_Count_Percent", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "HDPE_Length_Percent", "FLOAT")

    arcpy.AddField_management('Pipe_Stats', "Other_Count_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "Other_Length_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "Other_Count_Percent", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "Other_Length_Percent", "FLOAT")

    arcpy.AddField_management('Pipe_Stats', "DIP_Count_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "DIP_Length_Ac", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "DIP_Count_Percent", "FLOAT")
    arcpy.AddField_management('Pipe_Stats', "DIP_Length_Percent", "FLOAT")

    print "Done add_more_fields"

def calcs():
    #Calculates values for fields made in add_more_fields

    #Calculate total length of pipes and count per nbh or basin. All pipes were
    #assigned either a private or public distinction, so totals can be assigned
    #based on these fields
    arcpy.CalculateField_management("Pipe_Stats", "Total_Count", 
    "[Private_Count] + [Public_Count]", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "Total_Length", 
    "[Private_Length] + [Public_Length]", "VB")

    arcpy.CalculateField_management("Pipe_Stats", "Pipe_Count_Ac", 
    "round([Total_Count] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "Pipe_Length_Ac", 
    "round([Total_Length] / [Acres],1)", "VB")

    arcpy.CalculateField_management("Pipe_Stats", "Private_Count_Ac", 
    "round([Private_Count] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "Private_Length_Ac", 
    "round([Private_Length] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "Private_Count_Percent", 
    "round((([Private_Count] / [Total_Count])*100),1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "Private_Length_Percent", 
    "round((([Private_Length] / [Total_Length])*100),1)", "VB")

    arcpy.CalculateField_management("Pipe_Stats", "Public_Count_Ac", 
    "round([Public_Count] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "Public_Length_Ac", 
    "round([Public_Length] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "Public_Count_Percent", 
    "round((([Public_Count] / [Total_Count])*100),1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "Public_Length_Percent", 
    "round((([Public_Length] / [Total_Length])*100),1)", "VB")

    arcpy.CalculateField_management("Pipe_Stats", "Rehab_Count_Ac", 
    "round([Rehab_Count] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "Rehab_Length_Ac", 
    "round([Rehab_Length] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "Rehab_Count_Percent", 
    "round((([Rehab_Count] / [Total_Count])*100),1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "Rehab_Length_Percent", 
    "round((([Rehab_Length] / [Total_Length])*100),1)", "VB")

    arcpy.CalculateField_management("Pipe_Stats", "RCP_Count_Ac", 
    "round([RCP_Count] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "RCP_Length_Ac", 
    "round([RCP_Length] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "RCP_Count_Percent", 
    "round((([RCP_Count] / [Total_Count])*100),1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "RCP_Length_Percent", 
    "round((([RCP_Length] / [Total_Length])*100),1)", "VB")

    arcpy.CalculateField_management("Pipe_Stats", "VC_Count_Ac", 
    "round([VC_Count] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "VC_Length_Ac", 
    "round([VC_Length] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "VC_Count_Percent", 
    "round((([VC_Count] / [Total_Count])*100),1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "VC_Length_Percent", 
    "round((([VC_Length] / [Total_Length])*100),1)", "VB")

    arcpy.CalculateField_management("Pipe_Stats", "CMP_Count_Ac", 
    "round([CMP_Count] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "CMP_Length_Ac", 
    "round([CMP_Length] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "CMP_Count_Percent", 
    "round((([CMP_Count] / [Total_Count])*100),1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "CMP_Length_Percent", 
    "round((([CMP_Length] / [Total_Length])*100),1)", "VB")

    arcpy.CalculateField_management("Pipe_Stats", "PVC_Count_Ac", 
    "round([PVC_Count] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "PVC_Length_Ac", 
    "round([PVC_Length] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "PVC_Count_Percent", 
    "round((([PVC_Count] / [Total_Count])*100),1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "PVC_Length_Percent", 
    "round((([PVC_Length] / [Total_Length])*100),1)", "VB")

    arcpy.CalculateField_management("Pipe_Stats", "HDPE_Count_Ac", 
    "round([HDPE_Count] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "HDPE_Length_Ac", 
    "round([HDPE_Length] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "HDPE_Count_Percent", 
    "round((([HDPE_Count] / [Total_Count])*100),1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "HDPE_Length_Percent", 
    "round((([HDPE_Length] / [Total_Length])*100),1)", "VB")

    arcpy.CalculateField_management("Pipe_Stats", "DIP_Count_Ac", 
    "round([DIP_Count] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "DIP_Length_Ac", 
    "round([DIP_Length] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "DIP_Count_Percent", 
    "round((([DIP_Count] / [Total_Count])*100),1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "DIP_Length_Percent", 
    "round((([DIP_Length] / [Total_Length])*100),1)", "VB")

    arcpy.CalculateField_management("Pipe_Stats", "Other_Count_Ac", 
    "round([Other_Count] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "Other_Length_Ac", 
    "round([Other_Length] / [Acres],1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "Other_Count_Percent", 
    "round((([Other_Count] / [Total_Count])*100),1)", "VB")
    arcpy.CalculateField_management("Pipe_Stats", "Other_Length_Percent", 
    "round((([Other_Length] / [Total_Length])*100),1)", "VB")

    print "Done calcs"

initialize()
copy_basins() 
copy_nbhs()
clip_pipes()
stats()
add_field_stats() 
name_stats()
merge()
post_stats()
add_fields()
pop_fields()
clean_stats()
get_data()
clean()
round_vals()
null_zeros()
add_more_fields()
calcs()