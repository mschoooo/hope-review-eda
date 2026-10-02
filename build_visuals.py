from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
ASSET = ROOT / 'deck_assets'
ASSET.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'Malgun Gothic','axes.unicode_minus':False,'font.size':12})
df = pd.read_csv(ROOT/'hope_naver_reviews.csv', encoding='utf-8-sig', keep_default_na=False)
df['datetime'] = pd.to_datetime(df['작성일시'], format='%Y.%m.%d. %H:%M')
df['day'] = df['datetime'].dt.normalize()
df['low'] = df['평점'].le(3)

BG='#0b1020'; PANEL='#111a2e'; WHITE='#f7f8fb'; MUTED='#9aa7bd'; CYAN='#55d6be'; ORANGE='#ff8a5b'; BLUE='#62a0ea'; GRID='#263553'
def save(fig,name):
    fig.patch.set_facecolor(BG)
    for ax in fig.axes:
        ax.set_facecolor(PANEL); ax.tick_params(colors=MUTED); ax.xaxis.label.set_color(MUTED); ax.yaxis.label.set_color(MUTED); ax.title.set_color(WHITE)
        for s in ax.spines.values(): s.set_visible(False)
        ax.grid(axis='y', color=GRID, alpha=.6, linewidth=.8)
    fig.savefig(ASSET/name, dpi=180, bbox_inches='tight', facecolor=BG); plt.close(fig)

fig,ax=plt.subplots(figsize=(8,4.1))
for code,label,color in [('Y','실관람객',CYAN),('N','기타 리뷰',ORANGE)]:
    s=df[df['실관람객여부'].eq(code)]['평점'].value_counts(normalize=True).reindex(range(1,11),fill_value=0)*100
    ax.plot(range(1,11),s.values,marker='o',linewidth=3,markersize=6,label=label,color=color)
ax.set_xticks(range(1,11)); ax.set_xlabel('평점'); ax.set_ylabel('집단 내 비중 (%)'); ax.set_title('실관람객 집단은 10점 쏠림이 더 강하다',loc='left',fontweight='bold'); ax.legend(frameon=False,labelcolor=WHITE,ncol=2)
save(fig,'rating_distribution.png')

fig,ax=plt.subplots(figsize=(8,4.1))
bars=ax.bar(['전체 리뷰','공감 상위 100','순공감 상위 100'],[6.51,2.85,1.77],color=[BLUE,ORANGE,'#e05c4c'],width=.62)
ax.set_ylim(0,10); ax.set_ylabel('평균 평점'); ax.set_title('많이 공감된 리뷰는 전체보다 훨씬 부정적이다',loc='left',fontweight='bold')
for b,v in zip(bars,[6.51,2.85,1.77]): ax.text(b.get_x()+b.get_width()/2,v+.25,f'{v:.2f}',ha='center',color=WHITE,fontweight='bold')
save(fig,'visibility_bias.png')

patterns={'극장·체험':'극장|아이맥스|IMAX|아이맥|4D|4d|포디','공포·긴장':'공포|긴장|스릴','액션·추격':'액션|추격','연출·영상':'연출|영상|촬영|미장센','결말·개연성':'결말|개연성|스토리|서사','대사·욕설':'대사|욕설'}
topic=[]
for label,pat in patterns.items():
    g=df[df['리뷰'].str.contains(pat,regex=True,case=False)]
    topic.append((label,len(g),g['평점'].mean(),g['low'].mean()*100))
topic=sorted(topic,key=lambda x:x[2])
fig,ax=plt.subplots(figsize=(8,4.6)); y=np.arange(len(topic)); means=[x[2] for x in topic]; labels=[x[0] for x in topic]; colors=[ORANGE if x[0] in ['대사·욕설','결말·개연성'] else CYAN for x in topic]
ax.barh(y,means,color=colors,height=.56); ax.set_yticks(y,labels); ax.set_xlim(0,10); ax.set_xlabel('평균 평점'); ax.set_title('대사·개연성은 낮고, 체험·긴장감은 높다',loc='left',fontweight='bold')
for i,(label,n,m,low) in enumerate(topic): ax.text(m+.15,i,f'{m:.2f}  ·  {n:,}건',va='center',color=WHITE)
save(fig,'topic_ranking.png')

daily=df.groupby('day').agg(n=('평점','size'), mean=('평점','mean'))
fig,ax1=plt.subplots(figsize=(8,4.1)); ax2=ax1.twinx(); ax1.bar(daily.index,daily.n,color=BLUE,alpha=.8,width=.8); ax2.plot(daily.index,daily['mean'],color=ORANGE,linewidth=2.5); ax1.set_ylabel('리뷰 수',color=MUTED); ax2.set_ylabel('평균 평점',color=MUTED); ax2.set_ylim(0,10); ax1.set_title('첫날 반응이 가장 크고, 이후 평점은 완만히 상승한다',loc='left',fontweight='bold'); ax1.tick_params(axis='x',rotation=25)
save(fig,'daily_trend.png')
