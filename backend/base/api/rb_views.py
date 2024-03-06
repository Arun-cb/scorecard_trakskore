from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status, filters
import mysql.connector as sqlConnect
from .serializers import * 
import cx_Oracle


@api_view(["POST"])
def set_db_sql_connection(request):
    reqconnData = request.data
    print(reqconnData)
    mydb = sqlConnect.connect(
    host=reqconnData.get("host_id"), 
    user=reqconnData.get("user_name"),
    password=reqconnData.get("password"),
    database="score_card"
    # database=reqconnData.get("connection_name")
    )

    if mydb.is_connected():
        connect_message = "Connected"
        return Response(connect_message, status=status.HTTP_200_OK)
    else:
        error_message = "Not Connected"
        return Response(error_message,status=status.status.HTTP_400_BAD_REQUEST)
    

# Query Defnition
@api_view(["POST"])
def fnStoreQueryNameConnectionData (request):
    connnectionrequestdata = request.data

    postConnData = {
        "query_name" : connnectionrequestdata.get("queryName"),
        "connection_id" : connnectionrequestdata["savedConnectionItems"].get("id"),
        "query_text" : connnectionrequestdata["savedConnectionItems"].get("connection_name"),
        "created_by" : connnectionrequestdata["savedConnectionItems"].get("created_by"),
        "last_updated_by" : connnectionrequestdata["savedConnectionItems"].get("last_updated_by")
    }

    queryDefnitionSerilazier = qb_defnition_serializer(data=postConnData)
    
    if queryDefnitionSerilazier.is_valid():
        queryDefnitionSerilazier.save()
        return Response(queryDefnitionSerilazier.data,status = status.HTTP_201_CREATED)
    
    return Response(queryDefnitionSerilazier.errors,status = status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def fnGetQueryDefinition(request):
    queryDefinitionData = query_definition.objects.filter(delete_flag = "N")
    definitionSerializer = qb_defnition_serializer(queryDefinitionData,many=True)
    return Response(definitionSerializer.data,status = status.HTTP_200_OK)


# Selected Table
@api_view(["POST"])
def fnsaveSelectedTables (request):
    tableRequestData = request.data
    for i in range(len(tableRequestData)):
        selectedTableData = {
            "table_name": tableRequestData[i]["table_name"],
            "table_id" : tableRequestData[i]["id"],
            "query_id" : tableRequestData[i]["query_id"],
            "created_by" : tableRequestData[i]["created_by"],
            "last_updated_by" : tableRequestData[i]["last_updated_by"]
        }
        print(selectedTableData)
        
        querytableserilizer = qb_table_serializer(data= selectedTableData)

        if querytableserilizer.is_valid():
            querytableserilizer.save()
            
    return Response(querytableserilizer.data,status = status.HTTP_201_CREATED)


@api_view(["GET"])
def fnGetQueryBuilderTable(request):
    queryBuilderTable = query_builder_table.objects.filter(delete_flag = "N")
    builderTableSerializer = qb_table_serializer(queryBuilderTable,many=True)
    return Response(builderTableSerializer.data,status = status.HTTP_200_OK)

@api_view(["POST"])
def fnGetTableData(request):
    connnectionrequestdata = request.data
    print("connnectionrequestdata", connnectionrequestdata)
    mydb = sqlConnect.connect(
    host=connnectionrequestdata["savedConnectionItems"].get("host_id"), 
    user=connnectionrequestdata["savedConnectionItems"].get("user_name"),
    password=connnectionrequestdata["savedConnectionItems"].get("password"),
    database="score_card"
    # database=connnectionrequestdata["savedConnectionItems"].get("connection_name"),
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'score_card' AND table_type = 'BASE TABLE';")
    table_names = [{"id": idx, "table_name": table[0]} for idx, table in enumerate(mycursor.fetchall(), start=1)]
    return Response(table_names, status=status.HTTP_200_OK)


# Column Display , Insert and Get
@api_view(["POST"])
def rb_sql_show_columns(request):
    reqTableColumnData = request.data
    mydb = sqlConnect.connect(
    host="localhost", 
    user="root",
    password="",
    database="score_card"
    )

    allResults = []

    for table_info in reqTableColumnData:
        column_name = table_info['table_name']
        dbCursor = mydb.cursor()
        dbCursor.execute(f"SHOW COLUMNS FROM {column_name}")

        results = [{"id":idx,"columnName":row[0], "dataType":row[1].split('(')[0]} for idx,row in enumerate(dbCursor.fetchall(),start=1)]
        tableResults = {column_name:results}
        allResults.append(tableResults)

    return Response(allResults, status=status.HTTP_200_OK)


@api_view(["POST"])
def fnsaveSelectedColumn(request):
    reqColumnData = request.data
    for table_data in reqColumnData:
        for column_data in table_data["table_columns"]:
            postData={
                "table_column_query_id": table_data["query_id"],
                "column_name": column_data["columnName"],
                "table_column_table_id": column_data["tableId"],
                "created_by": table_data["created_by"],
                "last_updated_by": table_data["last_updated_by"],
            }
                        
            postcolumnserilizers = qb_table_columns_serializers(data=postData)
            
            if postcolumnserilizers.is_valid():
                postcolumnserilizers.save()
            
    return Response(postcolumnserilizers.data,status=status.HTTP_200_OK)


@api_view(["GET"])
def fngetsavedcolumns(request):
    savedcolumnsData = query_builder_table_columns.objects.filter(delete_flag = "N")
    saveColumnDataSerializers = qb_table_columns_serializers(savedcolumnsData,many=True)
    return Response(saveColumnDataSerializers.data,status = status.HTTP_200_OK)

# join table post and get

@api_view(["POST"])
def fninsjointablesave(request):
    reqjointabledata = request.data
    for i in range(len(reqjointabledata)):
        listofjointabledata ={
            "join_type" : reqjointabledata[i]["selectedAttribute"],
            "join_column_name1" : reqjointabledata[i]["selectedColumn"],
            "join_column_name2" : reqjointabledata[i]["selectedColumn2"],
            "tab_join_query_id" : reqjointabledata[i]["query_id"],
            "tab_join_table_id_one" : reqjointabledata[i]["tableid1"],
            "tab_join_table_id_two" : reqjointabledata[i]["tableid2"],
            "created_by" : reqjointabledata[i]["created_by"],
            "last_updated_by" : reqjointabledata[i]["last_updated_by"]
        }
        
        joinTableDataSerializers = qb_table_joins_serializers(data = listofjointabledata)
        
        if joinTableDataSerializers.is_valid():
            joinTableDataSerializers.save()
            
    return Response(joinTableDataSerializers.data,status=status.HTTP_200_OK)   


@api_view(["GET"])
def fnGetJoinTableColumnData(request):
    savedJoinTableColumData = query_builder_table_joins.objects.filter(delete_flag = "N")
    savedJoinTableSerializers = qb_table_joins_serializers(savedJoinTableColumData,many=True)
    return Response(savedJoinTableSerializers.data,status = status.HTTP_200_OK)
    

# Column Alias Post and Get
@api_view(["POST"])
def fn_ins_column_alias(request):
    requsetAliasData = request.data
    for i in range(len(requsetAliasData)):
        listofjointabledata ={
            "alias_name" : requsetAliasData[i]["setAliasName"],
            "col_alias_query_id" : requsetAliasData[i]["query_id"],
            "col_alias_table_id" : requsetAliasData[i]["aliastableId"],
            "col_alias_column_id" : requsetAliasData[i]["aliascolumnId"],
            "created_by" : requsetAliasData[i]["created_by"],
            "last_updated_by" : requsetAliasData[i]["last_updated_by"]
        }
        
        aliasTableDataSerializers = qb_table_alias_serializers(data = listofjointabledata)
        
        if aliasTableDataSerializers.is_valid():
            aliasTableDataSerializers.save()
            
    return Response(aliasTableDataSerializers.data,status=status.HTTP_200_OK)
    


@api_view(["GET"])
def fn_get_column_alias(request):
    savedAliasTableColumData = query_builder_table_alias.objects.filter(delete_flag = "N")
    savedAliasTableSerializers = qb_table_alias_serializers(savedAliasTableColumData,many=True)
    return Response(savedAliasTableSerializers.data,status = status.HTTP_200_OK)



@api_view(["POST"])
def fn_ins_column_aggregate(request):
    requestAggregateData = request.data
    for i in range(len(requestAggregateData)):
        listofaggregatetabledata ={
            "agg_fun_name" : requestAggregateData[i]["selectedAttribute"],
            "table_aggragate_query_id" : requestAggregateData[i]["query_id"],
            "table_aggregate_table_id" : requestAggregateData[i]["aggregatetableId"],
            "table_aggregate_column_id" : requestAggregateData[i]["aggregatecolumnId"],
            "created_by" : requestAggregateData[i]["created_by"],
            "last_updated_by" : requestAggregateData[i]["last_updated_by"]
        }
        
        
        aggregateserializers = qb_table_aggergate_serializers(data = listofaggregatetabledata)
        
        
        if aggregateserializers.is_valid():
            aggregateserializers.save()
        else:
            print(aggregateserializers.errors)
            
    return Response(aggregateserializers.data,status=status.HTTP_200_OK)
    


@api_view(["GET"])
def fn_get_column_aggregate(request):
    savedAggregatedTableColumData = query_builder_aggeration_function_table.objects.filter(delete_flag = "N")
    savedAggregatedTableSerializers = qb_table_aggergate_serializers(savedAggregatedTableColumData,many=True)
    return Response(savedAggregatedTableSerializers.data,status = status.HTTP_200_OK)


# Execute Query
@api_view(["POST"])
def fnpostquerytoexecute(request):
    queryText = request.data
    print(queryText)
    mydb = sqlConnect.connect(
    host="localhost", 
    user="root",
    password="",
    database="score_card"
    )
    
    
    dbCursor = mydb.cursor(dictionary = True)
    dbCursor.execute(queryText)
    columns = [column[0] for column in dbCursor.description]
    results = dbCursor.fetchall()
    response_data = [{'columns':columns,'data':results}]
    return Response(response_data,status=status.HTTP_200_OK)   



@api_view(["POST"])
def set_db_oracle_connection(request):
    mydb = cx_Oracle.connect('sys/Admin123@localhost:1521/orcl',mode=cx_Oracle.SYSDBA)
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM smpletable")
    columns = [col[0] for col in mycursor.description]
    results = [dict(zip(columns, row)) for row in mycursor.fetchall()]
    return Response(results, status=status.HTTP_200_OK)
