# crawler
to get stock info

select code,count(code) as num from portfolio_detail pd where pd.portfolio_type='SBJJ' group by pd.portfolio_type, pd.code order by num desc
