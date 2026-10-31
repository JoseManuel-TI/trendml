import sys
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_uci import prepare
from train_uci import temporal_split

class PreparationTests(unittest.TestCase):
    def test_cancellations_future_selection_and_duplicates(self):
        rows=[['1','12345','Original',5,'2011-01-01',2,1,'UK'],
              ['2','12345','Original',5,'2011-11-01',4,1,'UK'],
              ['C3','12345','Original',-5,'2011-11-02',4,1,'UK'],
              ['4','99999','Future bestseller',10000,'2011-11-02',10,1,'UK']]
        rows.append(rows[0])
        f=pd.DataFrame(rows,columns=['InvoiceNo','StockCode','Description','Quantity','InvoiceDate','UnitPrice','CustomerID','Country'])
        result=prepare(f,top=1)
        self.assertEqual(result['products'][0]['id'],'UCI-12345')
        self.assertEqual(result['preparation']['duplicate_rows_removed'],1)
        self.assertEqual(result['observations'][-1]['sold_quantity'],10)
        self.assertEqual(result['observations'][1]['daily_units'],0)
        self.assertEqual(result['observations'][1]['price'],2)
        self.assertNotIn('CustomerID',result['observations'][0])

    def test_temporal_purge_removes_overlapping_targets(self):
        frame=pd.DataFrame({'captured_at':pd.to_datetime(['2011-10-24','2011-10-30','2011-11-01']),
                            'target_at':pd.to_datetime(['2011-10-31','2011-11-06','2011-11-08'])})
        train,test=temporal_split(frame,'2011-11-01',['2011-11-01'])
        self.assertEqual(len(train),1)
        self.assertEqual(len(test),1)
        self.assertLessEqual(train.target_at.max(),test.captured_at.min())

if __name__=='__main__': unittest.main()
