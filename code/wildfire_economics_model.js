function wildfireModel(v={}) {
 const x={L:3674507475.328936,d:0.03,lag:5,life:10,K0:0.6,m:0.01,a:0.05,r:0.15,p:0.05,N:20,rho:0,...v};
 const {L,d,lag,life,K0,m,a,r,p,N,rho}=x;
 if(!(L>0&&d>=0&&lag>=5&&life>0&&K0>=0&&m>=0&&a>0&&a<=1&&p>0&&p<=.25&&N>=0&&rho>=0&&rho<1)) throw Error("Invalid model input");
 const g=x.g||Array(life).fill(1);
 if(g.length!==life||!Number.isInteger(life)||!Number.isInteger(N)||g.some(q=>!Number.isFinite(q)||q<0||q>1)||g.every(q=>q===0)) throw Error("Invalid maturity profile or discrete input");
 let F=0,G=0;
 for(let i=0;i<life;i++){const df=(1+d)**-(lag+i+1);F+=df;G+=df*g[i];}
 const kappa=K0/(1+d)**lag+m*F;
 const cbar=.25e6+.25*1e6/(1+d)+p*2e6/(1+d)**3;
 let P=0;
 if(N>0){
  if(rho===0) P=-Math.expm1(N*Math.log1p(-p));
  else {const c=1/rho-1,alpha=p*c,beta=(1-p)*c;let none=1;for(let i=0;i<N;i++)none*=(beta+i)/(alpha+beta+i);P=1-none;}
 }
 const C=N*cbar,D=kappa*a*L,gross=a*L*G*r,V=gross-D,W=P*Math.max(V,0)-C;
 const rmin=N>0?kappa/G+C/(P*L*G*a):null;
 const amin=N>0&&G*r>kappa?C/(P*L*(G*r-kappa)):null;
 return {...x,F,G,kappa,cbar,C,P,D,gross,V,W,rmin,theta:rmin===null?null:a*rmin,floor:kappa/G,amin};
}
function bestPortfolio(v={},b=1){
 let best={N:0,value:0};
 for(let n=1;n<=200;n++){const z=wildfireModel({...v,N:n});const value=z.P*Math.max(z.gross-b*z.D,0)-b*z.C;if(value>best.value)best={N:n,value};}
 return best;
}
function informationValue(pi=.6,se=.85,sp=.8,B=100,D=40,c=2){
 const before=Math.max(0,pi*B-D);
 const pos=pi*se+(1-pi)*(1-sp),neg=1-pos;
 const qpos=pos?pi*se/pos:0,qneg=neg?pi*(1-se)/neg:0;
 const after=pos*Math.max(0,qpos*B-D)+neg*Math.max(0,qneg*B-D);
 const perfect=pi*Math.max(0,B-D);
 return {prior_useful:pi,sensitivity:se,specificity:sp,benefit_useful:B,deployment_cost:D,study_cost:c,before,after,withStudy:after-c,EVSI:after-before,net:after-before-c,EVPI:perfect-before,pos,neg,qpos,qneg};
}
function cashDistribution(N=20){
 let mass=new Map([[0,1]]);
 for(let n=0;n<N;n++){
  const next=new Map();
  for(const [u,p] of mass)for(const [du,q] of [[1,.75],[5,.20],[13,.05]])next.set(u+du,(next.get(u+du)||0)+p*q);
  mass=next;
 }
 const rows=[...mass].sort((a,b)=>a[0]-b[0]).map(([u,p])=>({cost_m:u*.25,p}));
 let cum=0,q95=null;for(const z of rows){cum+=z.p;if(q95===null&&cum>=.95)q95=z.cost_m;}
 return {mean_m:rows.reduce((s,z)=>s+z.cost_m*z.p,0),q95_m:q95,worst_m:N*3.25,probability_over_mean:rows.filter(z=>z.cost_m>N*.6).reduce((s,z)=>s+z.p,0),rows};
}
function convexAdoption(eta=1){
 const z=wildfireModel(),a0=.05,a=a0*(z.G*z.r/((1+eta)*z.kappa))**(1/eta);
 const kappa=z.kappa*(a/a0)**eta,D=kappa*a*z.L,V=a*z.L*(z.G*z.r-kappa);
 return {eta,a,kappa,D,V,W:z.P*Math.max(V,0)-z.C};
}
const base=wildfireModel();
const specifications=[["Discount 2%",{"d":0.02}],["Base 3%",{}],["Discount 7%",{"d":0.07}],["Commissioning year 10",{"lag":10}],["Commissioning year 15",{"lag":15}],["Initial cost ratio 0.3",{"K0":0.3}],["Initial cost ratio 1.2",{"K0":1.2}],["Initial cost ratio 4.4",{"K0":4.4}],["Initial cost ratio 8.8",{"K0":8.8}],["Initial cost ratio 13.2",{"K0":13.2}],["Initial cost ratio 12",{"K0":12}],["Maintenance 0%",{"m":0}],["Maintenance 2%",{"m":0.02}],["Adoption 1%",{"a":0.01}],["Adoption 10%",{"a":0.1}],["Success 2.5%",{"p":0.025}],["Success 10%",{"p":0.1}],["Correlation 0.2",{"rho":0.2}],["Correlation 0.5",{"rho":0.5}],["Loss half fixed deployment cash",{"L":1837253737.664468,"K0":1.2,"m":0.02}],["Loss 1.5 times fixed deployment cash",{"L":5511761212.993404,"K0":0.39999999999999997,"m":0.006666666666666667}],["Maturation",{"g":[0.25,0.5,0.75,1,1,1,1,1,1,1]}],["California",{"L":1706431467.3970764}]];
const scenarios=specifications.map(([label,inputs])=>({label,...wildfireModel(inputs),optimum:bestPortfolio(inputs)}));
const comparators=[1,1.3,2,3].map(b=>({b,rmin:b*base.rmin,theta:b*base.theta,expected_resources:base.C+base.P*base.D,advantage:base.P*(base.gross-b*base.D)-b*base.C,optimum:bestPortfolio({},b)}));
const portfolios=[0,.2,.5].map(rho=>({rho,rows:Array.from({length:101},(_,N)=>wildfireModel({N,rho}))}));
const costCurves=[.01,.05,.1].map(a=>({a,rows:Array.from({length:141},(_,i)=>wildfireModel({a,K0:i/10}))}));
const adoptionCurves=[.3,.6,1.2].map(K0=>({K0,rows:Array.from({length:100},(_,i)=>wildfireModel({K0,a:(i+1)/1000}))}));

// Inverse targets use the same deployment model and fixed technical probabilities.
function commissioningCostLimit(z,b=1,r=z.r){
 if(!(b>0 && z.P>0))throw Error("Positive benchmark and discovery probability required");
 return (1+z.d)**z.lag*(z.G*r/b-z.m*z.F-z.C/(z.P*z.a*z.L));
}
const costComparison=[.6,4.4,8.8,13.2].map(K0=>{
 const z=wildfireModel({K0});
 return {K0,floor:z.floor,rmin:z.rmin,feasibleAtFullEffectiveness:z.rmin<=1,positiveAtAssumedEffectiveness:z.W>0};
});
const costTargets={
 effectiveness:base.r,
 commissioning_max_break_even:commissioningCostLimit(base),
 commissioning_max_b2:commissioningCostLimit(base,2),
 commissioning_max_full_effectiveness:commissioningCostLimit(base,1,1),
 comparator_ratio_reduction_low:1-commissioningCostLimit(base)/4.4,
 comparator_ratio_reduction_high:1-commissioningCostLimit(base)/13.2,
 commissioning_max_curve:Array.from({length:101},(_,i)=>({r:i/100,b1:commissioningCostLimit(base,1,i/100),b2:commissioningCostLimit(base,2,i/100)}))
};
const researchCeilings={
 discovery_probability_held_fixed:base.P,
 expected_research_pv_ceiling:base.P*Math.max(base.V,0),
 expected_research_pv_current:base.C,
 arithmetic_headroom_equals_reported_npv:base.P*Math.max(base.V,0)-base.C,
 b2_research_cost_allowance:base.P*(base.gross/2-base.D),
 b2_feasible_nonnegative_research_budget:base.gross/2-base.D>=0
};

const results={costComparison,costTargets,researchCeilings,base,scenarios,comparators,portfolios,costCurves,adoptionCurves,cash:cashDistribution(),convex:convexAdoption(),voi:informationValue()};
if(Math.abs(base.rmin-.09381139444507651)>1e-12)throw Error("Base threshold mismatch");
if(Math.abs(wildfireModel({r:base.rmin}).W)>1e-6)throw Error("Break-even identity");
if(bestPortfolio().N!==41)throw Error("Portfolio optimum");
if(Math.abs(results.voi.net-5.4)>1e-10)throw Error("Information value");
if(Math.abs(results.cash.mean_m-12)>1e-9||results.cash.q95_m!==18)throw Error("Cash distribution");

if(Math.abs(costTargets.commissioning_max_break_even-1.0793002008217136)>1e-7)throw Error("Cost ceiling mismatch");
if(Math.abs(wildfireModel({K0:costTargets.commissioning_max_break_even}).W)>1e-6)throw Error("Cost inverse identity");
if(Math.abs(researchCeilings.expected_research_pv_ceiling-base.C-base.W)>1e-6)throw Error("Research ceiling identity");
console.log(JSON.stringify(results,null,2));

