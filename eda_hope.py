from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'eda'; OUT.mkdir(exist_ok=True)
df=pd.read_csv(ROOT/'hope_naver_reviews.csv',encoding='utf-8-sig',keep_default_na=False,dtype={'리뷰ID':str,'영화코드':str})
df['datetime']=pd.to_datetime(df['작성일시'],format='%Y.%m.%d. %H:%M',errors='coerce')
df['day']=df.datetime.dt.normalize()
df['length']=df['리뷰'].fillna('').str.len()
df['low']=df['평점'].le(3); df['high']=df['평점'].ge(8)
df['net_votes']=df['공감수']-df['비공감수']
def stats(g):
    return {'n':len(g),'mean':float(g['평점'].mean()),'median':float(g['평점'].median()),'sd':float(g['평점'].std()),'low_pct':float(g.low.mean()*100),'high_pct':float(g.high.mean()*100),'one_pct':float(g['평점'].eq(1).mean()*100),'ten_pct':float(g['평점'].eq(10).mean()*100),'likes':int(g['공감수'].sum()),'dislikes':int(g['비공감수'].sum()),'median_likes':float(g['공감수'].median()),'mean_length':float(g.length.mean())}
report={'quality':{'rows':len(df),'missing':df.isna().sum().to_dict(),'duplicate_ids':int(df['리뷰ID'].duplicated().sum()),'duplicate_exact_text':int(df['리뷰'].duplicated().sum()),'empty_text':int(df['리뷰'].fillna('').str.strip().eq('').sum()),'invalid_ratings':int((~df['평점'].between(1,10)).sum()),'negative_votes':int((df[['공감수','비공감수']]<0).any(axis=1).sum()),'date_min':str(df.datetime.min()),'date_max':str(df.datetime.max())},'overall':stats(df)}
report['viewer']={k:stats(g) for k,g in df.groupby('실관람객여부')}
report['ratings']={str(k):int(v) for k,v in df['평점'].value_counts().sort_index().items()}
report['viewer_ratings']=pd.crosstab(df['평점'],df['실관람객여부']).to_dict()
daily=df.groupby('day').agg(n=('평점','size'),mean=('평점','mean'),viewer_pct=('실관람객여부',lambda x:x.eq('Y').mean()*100),low_pct=('low',lambda x:x.mean()*100),likes=('공감수','sum'))
report['first_day']=stats(df[df.day.eq(df.day.min())])
report['after_first_day']=stats(df[df.day.gt(df.day.min())])
report['weekly']={str(k):stats(g) for k,g in df.groupby(pd.Grouper(key='datetime',freq='W-WED')) if len(g)}
report['period_viewer']={f'{p}_{v}':stats(g) for (p,v),g in df.assign(period=np.where(df.day.eq(df.day.min()),'first_day','later')).groupby(['period','실관람객여부'])}
report['visibility']={}
for label,col in [('likes','공감수'),('net_votes','net_votes')]:
    top=df.nlargest(100,col)
    report['visibility'][label]={'top100':stats(top),'viewer_pct':float(top['실관람객여부'].eq('Y').mean()*100),'first_day_pct':float(top.day.eq(df.day.min()).mean()*100),'like_share_pct':float(top['공감수'].sum()/df['공감수'].sum()*100)}
report['visibility']['like_weighted_rating']=float(np.average(df['평점'],weights=df['공감수']))
report['visibility']['zero_like_pct']=float(df['공감수'].eq(0).mean()*100)
report['visibility']['top1pct_like_share']=float(df.nlargest(int(np.ceil(len(df)*.01)),'공감수')['공감수'].sum()/df['공감수'].sum()*100)
patterns={'대사':'대사|욕설','액션·추격':'액션|추격','연기':'연기|정호연','결말·개연성':'결말|개연성|스토리|서사','연출·영상':'연출|영상|촬영|미장센','공포·긴장':'공포|긴장|스릴','극장·체험':'극장|아이맥스|IMAX|아이맥|4D|4d|포디'}
report['topics']={}
for label,pat in patterns.items():
    mask=df['리뷰'].fillna('').str.contains(pat,regex=True,case=False)
    report['topics'][label]={**stats(df[mask]),'pct':float(mask.mean()*100),'viewer':{k:stats(g) for k,g in df[mask].groupby('실관람객여부')}}
report['duplicates_top']={k:int(v) for k,v in df['리뷰'].str.strip().value_counts().head(10).items()}
report['robustness']={}
for code,g in df.groupby('실관람객여부'):
    report['robustness'][code]={'top100_likes':stats(g.nlargest(100,'공감수')),'top100_net':stats(g.nlargest(100,'net_votes'))}
nonblank=df[df['리뷰'].str.strip().ne('')]
report['robustness']['nonblank']=stats(nonblank)
report['robustness']['nonblank_unique_text']=stats(nonblank.assign(clean_text=nonblank['리뷰'].str.strip()).drop_duplicates('clean_text'))
report['quality']['duplicate_nonblank_trimmed_text']=int(nonblank['리뷰'].str.strip().duplicated().sum())
(OUT/'metrics.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=int),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k not in ['weekly','topics','viewer_ratings','duplicates_top']},ensure_ascii=False,indent=2))
print('TOPICS',json.dumps({k:{z:v[z] for z in ['n','mean','low_pct','high_pct','pct']} for k,v in report['topics'].items()},ensure_ascii=False))
print('DAILY',daily.head(15).to_string())

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family']='Malgun Gothic';plt.rcParams['axes.unicode_minus']=False
fig,axs=plt.subplots(2,2,figsize=(13,9),layout='constrained')
colors={'Y':'#2878A0','N':'#DC8053'}
for code,label in [('Y','실관람객'),('N','기타 리뷰')]:
    g=df[df['실관람객여부'].eq(code)]
    dist=g['평점'].value_counts(normalize=True).reindex(range(1,11),fill_value=0)*100
    axs[0,0].plot(dist.index,dist.values,marker='o',label=label,color=colors[code])
axs[0,0].set(title='평점 분포: 집단 내 비중',xlabel='평점',ylabel='%');axs[0,0].legend();axs[0,0].set_xticks(range(1,11))
axs[0,1].bar(daily.index,daily.n,color='#2878A0');axs[0,1].set(title='일별 리뷰 수',ylabel='건');axs[0,1].tick_params(axis='x',rotation=30)
for code,label in [('Y','실관람객'),('N','기타 리뷰')]:
    g=df[df['실관람객여부'].eq(code)].groupby('day')['평점'].agg(['mean','size'])
    g.loc[g['size']<30,'mean']=np.nan
    g=g.reindex(pd.date_range(df.day.min(),df.day.max()))
    axs[1,0].plot(g.index,g['mean'],label=label,color=colors[code])
axs[1,0].set(title='일별 평균 평점 (집단별 30건 이상인 날)',ylabel='평점',ylim=(1,10));axs[1,0].legend();axs[1,0].tick_params(axis='x',rotation=30)
groups=[df,df.nlargest(100,'공감수'),df.nlargest(100,'net_votes')]
axs[1,1].bar(['전체 리뷰','공감 수 상위 100','순공감 상위 100'],[g['평점'].mean() for g in groups],color=['#2878A0','#DC8053','#B96748'])
axs[1,1].set(title='정렬 기준에 따른 평균 평점 차이',ylabel='평점',ylim=(0,10))
for i,g in enumerate(groups):axs[1,1].text(i,g['평점'].mean()+.15,f'{g["평점"].mean():.2f}',ha='center')
fig.suptitle('영화 호프 네이버 리뷰 EDA · 58,659건',fontsize=17)
fig.savefig(OUT/'hope_eda.png',dpi=160);plt.close(fig)
