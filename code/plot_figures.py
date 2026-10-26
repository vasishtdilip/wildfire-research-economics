import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'figures'
HERE.mkdir(exist_ok=True)
R=json.loads((ROOT/'outputs/model_results.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9.3,'axes.labelsize':10,'axes.titlesize':10.3,'xtick.labelsize':8.8,'ytick.labelsize':8.8,'legend.fontsize':8.7,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#444444','axes.linewidth':.7,'grid.color':'#dddddd','grid.linewidth':.5,'savefig.facecolor':'white','svg.fonttype':'none','pdf.fonttype':42})
BLUE='#205D89'; ORANGE='#B66118'; PURPLE='#76568A'; GREY='#696969'; LIGHT='#DCE7EF'
def style(ax):
    ax.set_axisbelow(True); ax.grid(axis='y',alpha=.8)
    ax.tick_params(length=3,width=.6)
def save(fig,name):
    fig.savefig(HERE/(name+'.png'),dpi=300,bbox_inches=None)
    fig.savefig(HERE/(name+'.svg'),bbox_inches=None)
    fig.savefig(HERE/(name+'.pdf'),bbox_inches=None)
    plt.close(fig)

# Figure 1
fig,ax=plt.subplots(figsize=(6.5,3.55),layout='constrained')
for series,color,ls in zip(R['portfolios'],[BLUE,ORANGE,PURPLE],['-','--',':']):
    rows=series['rows']; xx=[z['N'] for z in rows]; yy=[z['W']/1e6 for z in rows]
    rho=series['rho']; label='Independent projects' if rho==0 else f'Correlation ρ = {rho:.1f}'
    ax.plot(xx,yy,color=color,ls=ls,lw=1.9,label=label)
    best=max(rows,key=lambda z:z['W']); ax.scatter(best['N'],best['W']/1e6,color=color,s=24,zorder=5)
ax.axhline(0,color='#444444',lw=.8)
ax.set(xlim=(0,100),ylim=(-45,67),xlabel='Number of research projects',ylabel='Expected net present value (US$ million)')
ax.xaxis.set_major_locator(MultipleLocator(20)); style(ax)
ax.annotate('Maximum at 41 projects',xy=(41,58.724112422507),xytext=(48,63),fontsize=8.5,color=BLUE,arrowprops={'arrowstyle':'-','color':BLUE,'lw':.7})
ax.legend(loc='lower left',frameon=False,ncol=1)
save(fig,'figure1_portfolio')

# Figure 2
fig,axs=plt.subplots(1,2,figsize=(6.5,3.6),layout='constrained')
ax=axs[0]
for series,color,ls in zip(R['costCurves'],[ORANGE,BLUE,PURPLE],['--','-',':']):
    ax.plot([z['K0'] for z in series['rows']],[z['rmin']*100 for z in series['rows']],color=color,ls=ls,lw=1.65,label=f"Covered loss {series['a']*100:g}%")
ax.axhline(100,color=GREY,lw=.8,ls='--'); ax.axhspan(100,180,color='#F3F3F3',zorder=0)
ax.text(7,172,'Above 100% is infeasible',ha='center',fontsize=7.6,color=GREY)
ax.set(xlim=(0,14),ylim=(0,180),xlabel='Commissioning-cost ratio k₀ (years)',ylabel='Required effectiveness (%)',title='A  Commissioning costs')
ax.set_xticks([0,4.4,8.8,13.2]); ax.yaxis.set_major_locator(MultipleLocator(40)); style(ax)
ax.legend(loc='upper left',bbox_to_anchor=(0,.9),frameon=False,fontsize=7.8)
# Mark the base and external cost stress tests on the 5% adoption curve.
base_curve=next(z['rows'] for z in R['costCurves'] if z['a']==.05)
for cost,offset in [(.6,(22,7)),(4.4,(12,-15)),(8.8,(6,-17)),(13.2,(-38,10))]:
    point=min(base_curve,key=lambda z:abs(z['K0']-cost))
    ax.scatter(cost,point['rmin']*100,s=24,color=BLUE,edgecolor='white',linewidth=.6,zorder=5)
    label=('k₀ = 0.6: 9.38%' if cost==.6 else f"{point['rmin']*100:.1f}%")
    ax.annotate(label,xy=(cost,point['rmin']*100),xytext=offset,textcoords='offset points',fontsize=7.5,color=BLUE)
ax=axs[1]
for series,color,ls in zip(R['adoptionCurves'],[PURPLE,BLUE,ORANGE],[':','-','--']):
    ax.plot([z['a']*100 for z in series['rows']],[z['rmin']*100 for z in series['rows']],color=color,ls=ls,lw=1.65,label=f"k₀ = {series['K0']:g} years")
ax.axhline(100,color=GREY,lw=.8,ls='--')
ax.set(xlim=(0,10),ylim=(0,106),xlabel='Covered share of baseline loss (%)',title='B  Adoption scale')
ax.xaxis.set_major_locator(MultipleLocator(2)); ax.yaxis.set_major_locator(MultipleLocator(20)); style(ax)
ax.legend(loc='upper right',bbox_to_anchor=(1,.92),frameon=False,fontsize=7.8)
ax.scatter([5],[R['base']['rmin']*100],color=BLUE,s=20,zorder=5)
ax.annotate('Base case',xy=(5,R['base']['rmin']*100),xytext=(5.5,32),fontsize=7.8,color=BLUE,arrowprops={'arrowstyle':'-','color':BLUE,'lw':.7})
save(fig,'figure2_frontiers')

# Figure 3: exact model endpoints in Table 6 order.
sc={z['label']:z for z in R['scenarios']}; b=R['base']
factors=[
 ('Discount rate  2–7%',sc['Discount 2%'],sc['Discount 7%']),
 ('Commissioning  year 5–15',b,sc['Commissioning year 15']),
 ('Initial cost ratio  0.3–1.2 years',sc['Initial cost ratio 0.3'],sc['Initial cost ratio 1.2']),
 ('Maintenance  0–2%',sc['Maintenance 0%'],sc['Maintenance 2%']),
 ('Covered loss  1–10%',sc['Adoption 1%'],sc['Adoption 10%']),
 ('Success probability  2.5–10%',sc['Success 2.5%'],sc['Success 10%']),
 ('Technical correlation  0–0.5',b,sc['Correlation 0.5']),
 ('Loss estimate  0.5–1.5 × baseline¹',sc['Loss half fixed deployment cash'],sc['Loss 1.5 times fixed deployment cash']),
 ('Maturity  immediate–staged',b,sc['Maturation'])]
fig,ax=plt.subplots(figsize=(6.5,4.35),layout='constrained')
for i,(label,lo,hi) in enumerate(factors):
    ys=len(factors)-i-1; ends=[lo['rmin']*100,hi['rmin']*100]
    ax.plot(ends,[ys,ys],color=BLUE,lw=4,solid_capstyle='round')
    ax.scatter(ends,[ys,ys],s=14,color=BLUE,zorder=3)
ax.axvline(b['rmin']*100,color=ORANGE,lw=1.25,ls='--',label='Base case 9.381%')
ax.set_yticks(range(len(factors))); ax.set_yticklabels([f[0] for f in factors][::-1])
ax.set(xlim=(4.5,20),ylim=(-.65,8.65),xlabel='Required effectiveness (%)')
ax.tick_params(axis='y',length=0,pad=7); ax.xaxis.set_major_locator(MultipleLocator(2))
ax.spines['left'].set_visible(False); ax.grid(axis='x',color='#dddddd',lw=.5);ax.set_axisbelow(True)
ax.legend(frameon=False,loc='lower right',fontsize=8.5)
fig.get_layout_engine().set(rect=(0,.05,1,.94))
fig.text(.015,.012,'¹ Physical commissioning and maintenance spending held fixed.',fontsize=8,color='#555555')
save(fig,'figure3_sensitivity')

# Figure 4
fig,axs=plt.subplots(1,2,figsize=(6.5,3.55),layout='constrained')
ax=axs[0]; labels=['No study','Information\nbefore study cost','After\nstudy cost']; values=[R['voi']['before'],R['voi']['after'],R['voi']['withStudy']]
bars=ax.bar(range(3),values,width=.62,color=[GREY,LIGHT,BLUE],edgecolor=[GREY,BLUE,BLUE],linewidth=.8)
for i,v in enumerate(values): ax.text(i,v+.65,f'{v:g}',ha='center',fontsize=9)
ax.set_xticks(range(3)); ax.set_xticklabels(labels,fontsize=8)
ax.set(ylim=(0,33),ylabel='Expected net value (US$ million)',title='A  Value of the decision')
ax.yaxis.set_major_locator(MultipleLocator(10));style(ax)
ax=axs[1]; values=[12.8,-5.4,-2,5.4]; bottoms=[0,12.8,7.4,0]
labels=['Avoided bad\ndeployment','Useful value\nlost¹','Study\ncost','Net value\nof study']
colors=[BLUE,ORANGE,GREY,BLUE]
for i,(v,bot,col) in enumerate(zip(values,bottoms,colors)):
    ax.bar(i,v,bottom=bot,width=.62,color=col)
    if i<3: ax.plot([i+.31,i+.69],[bot+v,bot+v],color=GREY,lw=.65,ls=':')
    ax.text(i,(bot+v+.6) if v>0 else (bot+v/2),f'{v:+g}' if i<3 else f'{v:g}',ha='center',va='bottom' if v>0 else 'center',fontsize=8.5,color='white' if v<0 else '#111111')
ax.axhline(0,color=GREY,lw=.7)
ax.set_xticks(range(4));ax.set_xticklabels(labels,fontsize=7.0)
ax.set(ylim=(0,15),title='B  Net value contributions',ylabel='Contribution (US$ million)')
ax.yaxis.set_major_locator(MultipleLocator(5));style(ax)
fig.get_layout_engine().set(rect=(0,.08,1,.91))
fig.text(.015,.012,'¹ Useful deployment opportunities lost to false-negative test results.',fontsize=8,color='#555555')
save(fig,'figure4_information_value')

assert abs(b['rmin']*100-9.381139444507651)<1e-9
assert abs(R['voi']['after']-27.4)<1e-9
print('Saved four figures as PNG, SVG and PDF; model identities passed.')
