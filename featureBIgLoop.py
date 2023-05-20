import pandas as pd
import gc

dirThis = 'C:\\Users\\chcww\\Downloads\\'

offers = pd.read_csv(dirThis + 'offers.csv')
#transactions = pd.read_csv(r'/content/drive/MyDrive/1經濟學/專題/newdata.csv')
trainHistory = pd.read_csv(dirThis + 'trainHistory.csv')
testHistory = pd.read_csv(dirThis + 'testHistory.csv')

tranDtype = {
    'id': 'uint64',
    'chain': 'uint16',
    'dept': 'uint8',
    'category': 'uint16',
    'company': 'uint64',
    'brand': 'uint32',
    'date' : 'object',
    'productsize': 'float32',
    'productmeasure': 'category',
    'purchasequantity': 'int64',
    'purchaseamount': 'float32'
    }


def generateFeature(offers, transactions, trainHistory, testHistory, tidx) :
    # import useful package
    from datetime import timedelta
    from itertools import cycle
    import pandas as pd
    import numpy as np
    import time
    import gc
    ts = time.time()
    # tk = 1
    
    # get all data & delete those not in transactions
    train = trainHistory.drop(columns = ['repeater', 'repeattrips'])
    data = pd.concat([train, testHistory], axis=0, ignore_index=True)
    use = data[data['id'].isin(transactions['id'])] # (310665, )

    del trainHistory, train, testHistory
    gc.collect()
    
    # te = time.time()
    # print('Inner -', str(tidx) + ' of ' + str(tk) + '(get all data) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
    # tk+=1
    
    # put offer information into transactions
    of = offers[['offer', 'category', 'company', 'offervalue', 'brand']]
    usf = pd.merge(use, of, on='offer')
    usf.columns = ['id', 'chain', 'offer', 'market', 'offerdate', 'offercategory', 'offercompany',
          'offervalue', 'offerbrand']
    tu = usf[['id', 'offer', 'offerdate', 'offercategory', 'offercompany', 'offerbrand']]
    nu = pd.merge(tu, transactions, on='id')
    
    del tu, usf, of, transactions
    gc.collect()
    
    # te = time.time()
    # print('Inner -', str(tidx) + ' of ' + str(tk) + '(put offer information) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
    # tk+=1
    
    # generate time index
    date_format = '%Y-%m-%d'
    nu['offerdate'] = pd.to_datetime(nu['offerdate'], format = date_format)
    # nu['date'] = pd.to_datetime(nu['date'], format = date_format)
    nu['daydiff'] = nu['offerdate'] - nu['date']
    nu['diff_180'] = nu['offerdate'] - timedelta(days = 180)
    nu['diff_150'] = nu['offerdate'] - timedelta(days = 150)
    nu['diff_120'] = nu['offerdate'] - timedelta(days = 120)
    nu['diff_90'] = nu['offerdate'] - timedelta(days = 90)
    nu['diff_60'] = nu['offerdate'] - timedelta(days = 60)
    nu['diff_30'] = nu['offerdate'] - timedelta(days = 30)
    
    # te = time.time()
    # print('Inner -', str(tidx) + ' of ' + str(tk) + '(generate time index) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
    # tk+=1
    
    # put offervalue
    of1 = offers[['offer', 'offervalue']]
    use = pd.merge(use, of1, on='offer')
    
    # te = time.time()
    # print('Inner -', str(tidx) + ' of ' + str(tk) + '(put offervalue) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
    # tk+=1
    
    # generate total
    group = nu.groupby(['id'])
    
    test = group['chain'].count().reset_index()
    test.columns = ['id', 'buy_total_freq']
    use = pd.merge(use, test, on='id')
    
    # te = time.time()
    # print('Inner -', str(tidx) + ' of ' + str(tk) + '(generate total freq) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
    # tk+=1
    
    test = group['purchaseamount'].sum().reset_index()
    test.columns = ['id', 'buy_total_amount']
    use = pd.merge(use, test, on='id')
    
    # te = time.time()
    # print('Inner -', str(tidx) + ' of ' + str(tk) + '(generate total amount) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
    # tk+=1
    
    test = group['purchaseamount'].mean().reset_index()
    test.columns = ['id', 'buy_total_avgamount']
    use = pd.merge(use, test, on='id')
    
    # te = time.time()
    # print('Inner -', str(tidx) + ' of ' + str(tk) + '(generate total avg) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
    # tk+=1
    
    test = group['purchasequantity'].sum().reset_index()
    test.columns = ['id', 'buy_total_quantity']
    use = pd.merge(use, test, on='id')
    
    # te = time.time()
    # print('Inner -', str(tidx) + ' of ' + str(tk) + '(generate total quan) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
    # tk+=1
    
    test = group['daydiff'].min().reset_index()
    test.columns = ['id', 'buy_total_daydiff']
    use = pd.merge(use, test, on='id')
    
    # te = time.time()
    # print('Inner -', str(tidx) + ' of ' + str(tk) + '(generate total) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
    # tk+=1
    
    
    day = np.linspace(30, 180, 6, endpoint=True).astype(int).astype(str)
    
    for i in day :
      daa = 'diff_' + i
      nu['ascom'] = nu['date'] >= nu[daa]
    
      name = 'buy_total_amount_' + i
      var = 'purchaseamount'
    
      group = nu.groupby(['id', 'ascom'])
      test = group[var].sum().reset_index()
      test.columns = ['id', 'ascom', name]
      use = pd.merge(use, test[test['ascom']][['id', name]], on='id', how = 'outer')
    
      # te = time.time()
      # print('Inner -', str(tidx) + ' of ' + str(tk) + '(generate day amount) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
      # tk+=1
    
      name = 'buy_total_quantity_' + i
      var = 'purchasequantity'
    
      group = nu.groupby(['id', 'ascom'])
      test = group[var].sum().reset_index()
      test.columns = ['id', 'ascom', name]
      use = pd.merge(use, test[test['ascom']][['id', name]], on='id', how = 'outer')
    
      # te = time.time()
      # print('Inner -', str(tidx) + ' of ' + str(tk) + '(generate day quan) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
      # tk+=1
    
      name = 'buy_total_freq_' + i
      var = 'purchaseamount'
    
      group = nu.groupby(['id', 'ascom'])
      test = group['chain'].count().reset_index()
      test.columns = ['id', 'ascom', name]
      use = pd.merge(use, test[test['ascom']][['id', name]], on='id', how = 'outer')
    
      # te = time.time()
      # print('Inner -', str(tidx) + ' of ' + str(tk) + '(generate day) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
      # tk+=1
    
    # generate company & brand & category
    mea = ['company', 'brand', 'category']
    day = np.repeat(np.linspace(30, 180, 6, endpoint=True), 3).astype(int).astype(str)
    
    for i in mea :
      nu['ascom'] = nu[i] == nu['offer' + i]
      group = nu.groupby(['id', 'ascom'])
    
      test = group['chain'].count().reset_index()
      test.columns = ['id', 'ascom', 'buy_'+i+'_freq']
      use = pd.merge(use, test[test['ascom']][['id', 'buy_'+i+'_freq']], on='id', how = 'outer')
    
      # te = time.time()
      # print('Inner -', str(tidx) + ' of ' + str(tk) + '(generate other freq) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
      # tk+=1
    
      test = group['purchaseamount'].sum().reset_index()
      test.columns = ['id', 'ascom', 'buy_'+i+'_amount']
      use = pd.merge(use, test[test['ascom']][['id', 'buy_'+i+'_amount']], on='id', how = 'outer')
    
      # te = time.time()
      # print('Inner -', str(tidx) + ' of ' + str(tk) + '(generate other amount) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
      # tk+=1
    
      test = group['purchaseamount'].mean().reset_index()
      test.columns = ['id', 'ascom', 'buy_'+i+'_avgamount']
      use = pd.merge(use, test[test['ascom']][['id', 'buy_'+i+'_avgamount']], on='id', how = 'outer')
    
      # te = time.time()
      # print('Inner -', str(tidx) + ' of ' + str(tk) + '(generate other avg) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
      # tk+=1
    
      test = group['purchasequantity'].sum().reset_index()
      test.columns = ['id', 'ascom', 'buy_'+i+'_quantity']
      use = pd.merge(use, test[test['ascom']][['id', 'buy_'+i+'_quantity']], on='id', how = 'outer')
    
      # te = time.time()
      # print('Inner -', str(tidx) + ' of ' + str(tk) + '(generate other quan) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
      # tk+=1
    
      test = group['daydiff'].min().reset_index()
      test.columns = ['id', 'ascom', 'buy_'+i+'_daydiff']
      use = pd.merge(use, test[test['ascom']][['id', 'buy_'+i+'_daydiff']], on='id', how = 'outer')
    
      # te = time.time()
      # print('Inner -', str(tidx) + ' of ' + str(tk) + '(generate other) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
      # tk+=1
    
    
    for i, j in zip(day, cycle(mea)) :
      daa = 'diff_' + i
      nu['ascom'] = ((nu['date'] >= nu[daa]) & (nu[j] == nu['offer' + j]))
    
      name = 'buy_'+j+'_amount_' + i
      var = 'purchaseamount'
    
      group = nu.groupby(['id', 'ascom'])
      test = group[var].sum().reset_index()
      test.columns = ['id', 'ascom', name]
      use = pd.merge(use, test[test['ascom']][['id', name]], on='id', how = 'outer')
    
      # te = time.time()
      # print('Inner -', str(tidx) + ' of ' + str(tk) + '(generate other day amount) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
      # tk+=1
    
      name = 'buy_'+j+'_quantity_' + i
      var = 'purchasequantity'
    
      group = nu.groupby(['id', 'ascom'])
      test = group[var].sum().reset_index()
      test.columns = ['id', 'ascom', name]
      use = pd.merge(use, test[test['ascom']][['id', name]], on='id', how = 'outer')
    
      # te = time.time()
      # print('Inner -', str(tidx) + ' of ' + str(tk) + '(generate other day quan) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
      # tk+=1
    
      name = 'buy_'+j+'_freq_' + i
      var = 'purchaseamount'
    
      group = nu.groupby(['id', 'ascom'])
      test = group['chain'].count().reset_index()
      test.columns = ['id', 'ascom', name]
      use = pd.merge(use, test[test['ascom']][['id', name]], on='id', how = 'outer')
    
      # te = time.time()
      # # print('Inner -', str(tidx) + ' of ' + str(tk) + '(generate other day) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
      # # tk+=1
    
    # generate not buy index
    nu['ascom'] = (nu['company'] == nu['offercompany']) & (nu['brand'] == nu['offerbrand']) & (nu['category'] == nu['offercategory'])
    group = nu.groupby(['id', 'ascom'])

    name1 = 'buy_company_brand_category'
    name = name1 + '_freq'

    test = group['chain'].count().reset_index()
    test.columns = ['id', 'ascom', name]
    use = pd.merge(use, test[test['ascom']][['id', name]], on='id', how = 'outer')
    new = pd.DataFrame((use[name] > 0) != True)
    new.columns = ['not_' + name1]
    use = pd.concat([use, new], axis = 1)



    nu['ascom'] = (nu['company'] == nu['offercompany']) & (nu['brand'] == nu['offerbrand'])
    group = nu.groupby(['id', 'ascom'])

    name1 = 'buy_company_brand'
    name = name1 + '_freq'

    test = group['chain'].count().reset_index()
    test.columns = ['id', 'ascom', name]
    use = pd.merge(use, test[test['ascom']][['id', name]], on='id', how = 'outer')
    new = pd.DataFrame((use[name] > 0) != True)
    new.columns = ['not_' + name1]
    use = pd.concat([use, new], axis = 1)



    nu['ascom'] = (nu['company'] == nu['offercompany']) & (nu['category'] == nu['offercategory'])
    group = nu.groupby(['id', 'ascom'])

    name1 = 'buy_company_category'
    name = name1 + '_freq'

    test = group['chain'].count().reset_index()
    test.columns = ['id', 'ascom', name]
    use = pd.merge(use, test[test['ascom']][['id', name]], on='id', how = 'outer')
    new = pd.DataFrame((use[name] > 0) != True)
    new.columns = ['not_' + name1]
    use = pd.concat([use, new], axis = 1)



    nu['ascom'] = (nu['brand'] == nu['offerbrand']) & (nu['category'] == nu['offercategory'])
    group = nu.groupby(['id', 'ascom'])

    name1 = 'buy_brand_category'
    name = name1 + '_freq'

    test = group['chain'].count().reset_index()
    test.columns = ['id', 'ascom', name]
    use = pd.merge(use, test[test['ascom']][['id', name]], on='id', how = 'outer')
    new = pd.DataFrame((use[name] > 0) != True)
    new.columns = ['not_' + name1]
    use = pd.concat([use, new], axis = 1)

    del new
    gc.collect()

    new1 = pd.DataFrame((use['buy_company_freq'] > 0) != True)
    new1.columns = ['not_buy_company']
    new2 = pd.DataFrame((use['buy_brand_freq'] > 0) != True)
    new2.columns = ['not_buy_brand']
    new3 = pd.DataFrame((use['buy_category_freq'] > 0) != True)
    new3.columns = ['not_buy_category']
    use = pd.concat([use, new1, new2, new3], axis = 1)

    del new1, new2, new3
    gc.collect()

    # handle na problem
    dayVar = ['buy_company_daydiff', 'buy_brand_daydiff', 'buy_category_daydiff', 'buy_total_daydiff']
    use1 = use[dayVar]
    use.drop(columns = dayVar, inplace = True)
    use = use.fillna(0)
    use1 = use1.fillna(timedelta(0))
    use = pd.concat([use, use1], axis = 1)

    del use1
    gc.collect()
    
    # te = time.time()
    # print('Inner -', str(tidx) + ' of ' + str(tk) + '(handle na problem) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
    # tk+=1
    
    # transform date type into int
    for i in use[dayVar] :
      use[i] = use[i].astype('str').apply(lambda x:x[:-5]).astype('int32')
    
    # te = time.time()
    # print('Inner -', str(tidx) + ' of ' + str(tk) + '(transform date type) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
    # tk+=1
    
    # transform bool type into int
    for i in use.columns :
      if(use[i].dtypes == 'bool') :
        use[i] = use[i].apply(int)
    
    te = time.time()
    print('Inner -', str(tidx) + ' (generate feature) -> time elapsed: ' + str(round(te-ts, 2)) + ' seconds')
    
    return use


def find_index(data_col, val):
    val_list = []
    
    val_list.append(val)
    val_list.append("end")

    index = data_col.isin(val_list).idxmax()
    
    return index


# =============================================================================
# Start Generate
# =============================================================================

import time
t1 = time.time()

startNode = [1, 9998981, 19997377, 29996610, 39995441, 49995224,
             59994902, 69994370, 79992981, 89992819, 99991845,
             109990375, 119989984, 129989664, 139989218, 149988698,
             159988143, 169987938, 179987039, 189986963, 199986166,
             208917355, 218916000, 228915444, 238915248, 248915214,
             258914236]

to = 1
bc = True
row = 10000000
end = 349655789
Start = []
End = []

while(to < 2) :
    tm = 1
    
    t2 = time.time()
    idx = startNode[to-1]
    idx1 = startNode[to] - idx

    if(end+1-idx <= row) :
      bc = False
      row = end+1-idx
      t2 = time.time()
      print('Stage -', str(to) + ' of ' + '(LASTTT) -> time elapsed: ' + str(round(t2-t1, 2)) + ' seconds' \
            + '\n\nStart : ' + str(idx) + ' End : ' + str(idx+row-1) + '\n')
      tm+=1

    print('\nStage -', str(to) + ' of ' + str(tm) + '(start) -> time elapsed: ' + str(round(t2-t1, 2)) + ' seconds')
    tm+=1
    
    # # from dask import dataframe as dd
    # transactions = pd.read_csv(
    #     dirThis + 'transactions.csv', 
    #     names=['id', 'chain', 'dept', 'category', 'company', 'brand', 'date', \
    #            'productsize', 'productmeasure', 'purchasequantity', 'purchaseamount'],
    #     dtype = tranDtype,
    #     nrows = row,
    #     parse_dates=['date'],
    #     infer_datetime_format=True,
    #     skiprows = idx,
    #     # engine = "pyarrow",
    #     # engine = "python-fwf",
    #     engine = "c"
    #     # blocksize=64000000 # = 64 Mb chunks
    # )
    
    if(bc) :
        # idx1 = find_index(transactions['id'], int(transactions['id'].loc[len(transactions['id']) - 1]))
        
        # del transactions
        # gc.collect()
        
        t2 = time.time()
        print('Stage -', str(to) + ' of ' + str(tm) + '(read data) -> time elapsed: ' + str(round(t2-t1, 2)) + ' seconds')
        tm+=1
        
        transactions = pd.read_csv(
            dirThis + 'transactions.csv', 
            names=['id', 'chain', 'dept', 'category', 'company', 'brand', 'date', \
                    'productsize', 'productmeasure', 'purchasequantity', 'purchaseamount'],
            dtype = tranDtype,
            nrows = idx1,
            parse_dates=['date'],
            infer_datetime_format=True,
            skiprows = idx,
            # engine = "pyarrow",
            # engine = "python-fwf",
            engine = "c"
            # blocksize=64000000 # = 64 Mb chunks
        )
    
    t2 = time.time()
    print('Stage -', str(to) + ' of ' + str(tm) + '(reRead data) -> time elapsed: ' + str(round(t2-t1, 2)) + ' seconds')
    print('\n# =============================================================================')
    print('#                 Start : ' + str(idx) + '  >>>>>  End : ' + str(idx+idx1-1))
    print('# =============================================================================\n')
    tm+=1

    Start.append(idx)
    End.append(idx+idx1-1)
    
    # idx += idx1
      
    use = generateFeature(offers, transactions, trainHistory, testHistory, to)

    del transactions
    gc.collect()
    
    t2 = time.time()
    print('Stage -', str(to) + ' of ' + str(tm) + '(generate) -> time elapsed: ' + str(round(t2-t1, 2)) + ' seconds')
    tm+=1
    
    use.to_csv(dirThis + 'split' + str(to) + '.csv')
    
    
    del use
    
    t2 = time.time()
    print('Stage -', str(to) + ' of ' + str(tm) + '(ouput) -> time elapsed: ' + str(round(t2-t1, 2)) + ' seconds\n')
    print('# =============================================================================')
    gc.collect()
    tm+=1
    to+=1

print("Finish!!!!!")


# use.shape
# use.isna().sum().sum()
# for i in use.columns :
#    print(i)