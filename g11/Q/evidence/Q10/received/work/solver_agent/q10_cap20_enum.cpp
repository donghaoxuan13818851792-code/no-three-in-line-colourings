// Exact enumeration of arbitrary size-20 caps compatible with a fixed Q10
// size-22 anchor and the residual four-colour line-capacity condition.
#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using U128=unsigned __int128;
constexpr int N=11,P=121;constexpr U128 FULL=(U128(1)<<P)-1;
int pc(U128 x){return std::popcount((uint64_t)x)+std::popcount((uint64_t)(x>>64));}
int low(U128 x){uint64_t a=(uint64_t)x;if(a)return std::countr_zero(a);uint64_t b=(uint64_t)(x>>64);return b?64+std::countr_zero(b):-1;}
int high(U128 x){uint64_t b=(uint64_t)(x>>64);if(b)return 127-std::countl_zero(b);uint64_t a=(uint64_t)x;return a?63-std::countl_zero(a):-1;}
U128 parse(const std::string&s){if(s.size()!=31)throw std::runtime_error("hex length");U128 x=0;for(char ch:s){int d=ch>='0'&&ch<='9'?ch-'0':ch>='a'&&ch<='f'?ch-'a'+10:ch>='A'&&ch<='F'?ch-'A'+10:-1;if(d<0)throw std::runtime_error("hex digit");x=(x<<4)|d;}if(x&~FULL)throw std::runtime_error("outside grid");return x;}
std::string dec(U128 x){if(!x)return"0";std::string s;while(x){s.push_back('0'+x%10);x/=10;}std::reverse(s.begin(),s.end());return s;}
std::string hex(U128 x){static constexpr char d[]="0123456789abcdef";std::string s(31,'0');for(int i=30;i>=0;--i){s[i]=d[(int)(x&15)];x>>=4;}return s;}
std::vector<std::pair<int,int>> pairs(){std::vector<std::pair<int,int>>v;for(int a=0;a<N;++a)for(int b=a+1;b<N;++b)v.push_back({a,b});return v;}
struct Tight{U128 mask;uint8_t lower;};
struct Pattern{U128 mask;uint8_t a,b;};
struct Enum{
 U128 anchor,residual,chosen=0,blocked=0,total=0,extendible=0,least_eligible=0;
 std::vector<U128>frozen_caps;std::ofstream masks_out;
 std::array<std::array<U128,P>,P>sec{};
 std::vector<U128>all_lines;
 std::array<std::vector<int>,N>rowpts;
 std::array<std::vector<Pattern>,N>patterns;
 std::vector<Tight>tight;
 std::array<uint8_t,N>rowtarget{},coltarget{},colcnt{};
 uint16_t assigned=0;uint64_t nodes=0,leaves=0,line_rejects=0,col_rejects=0,self_secant_rejects=0;
 double limit=0;bool stopped=false;std::chrono::steady_clock::time_point start;
 Enum(U128 a,int rp,int cp,double lim,std::vector<U128>caps,const std::string&output):anchor(a),residual(FULL&~a),frozen_caps(std::move(caps)),limit(lim){
  if(pc(a)!=22)throw std::runtime_error("anchor size");auto ps=pairs();if(rp<0||rp>=55||cp<0||cp>=55)throw std::runtime_error("pair id");
  rowtarget.fill(2);coltarget.fill(2);rowtarget[ps[rp].first]=rowtarget[ps[rp].second]=1;coltarget[ps[cp].first]=coltarget[ps[cp].second]=1;
  for(int p=0;p<P;++p)if((residual>>p)&1)rowpts[p/N].push_back(p);
  for(int r=0;r<N;++r){auto&v=rowpts[r];if(v.size()!=9)throw std::runtime_error("anchor row");if(rowtarget[r]==1){for(int p:v)patterns[r].push_back({U128(1)<<p,(uint8_t)p,255});}else for(int i=0;i<9;++i)for(int j=i+1;j<9;++j)patterns[r].push_back({(U128(1)<<v[i])|(U128(1)<<v[j]),(uint8_t)v[i],(uint8_t)v[j]});}
  std::set<U128>lines;
  for(int x=0;x<P;++x)for(int y=x+1;y<P;++y){int rx=x/N,cx=x%N,ry=y/N,cy=y%N;U128 m=0;for(int p=0;p<P;++p){int r=p/N,c=p%N;if((ry-rx)*(c-cx)==(cy-cx)*(r-rx))m|=U128(1)<<p;}if(pc(m)>=3)lines.insert(m);sec[x][y]=sec[y][x]=m;}
  if(lines.size()!=628)throw std::runtime_error("geometry");
  all_lines.assign(lines.begin(),lines.end());
  for(U128 m:all_lines){int lo=pc(m)-pc(m&anchor)-8;if(lo>0)tight.push_back({m,(uint8_t)lo});}
  if(!output.empty()){masks_out.open(output);if(!masks_out)throw std::runtime_error("open output masks");}
 }
 bool budget(){if((nodes&16383)==0&&limit>0&&std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>=limit){stopped=true;return false;}return true;}
 bool compatible(const Pattern&p)const{if(p.mask&blocked)return false;if(colcnt[p.a%N]>=coltarget[p.a%N])return false;if(p.b!=255&&colcnt[p.b%N]>=coltarget[p.b%N])return false;return true;}
 bool feasible()const{
  for(int c=0;c<N;++c){int av=0;for(int r=0;r<N;++r)if(!(assigned&(1u<<r))){int p=N*r+c;if(((residual>>p)&1)&&!((blocked>>p)&1))++av;}if(colcnt[c]+av<coltarget[c])return false;}
  for(auto&t:tight){int have=pc(chosen&t.mask),av=0;U128 x=t.mask&residual&~blocked;while(x){int p=low(x);x&=x-1;if(!(assigned&(1u<<(p/N)))&&colcnt[p%N]<coltarget[p%N])++av;}if(have+av<t.lower)return false;}
  return true;
 }
 void dfs(int depth){
  ++nodes;if(!budget())return;if(depth==N){
   ++leaves;
   if(pc(chosen)!=20)throw std::runtime_error("leaf size");
   if(chosen&anchor)throw std::runtime_error("leaf intersects anchor");
   for(int c=0;c<N;++c)if(colcnt[c]!=coltarget[c])throw std::runtime_error("leaf col");
   // Independent terminal guard: incremental secant blocking is an optimization,
   // while this direct scan of every maximal line is the acceptance criterion.
   for(U128 m:all_lines)if(pc(chosen&m)>2)throw std::runtime_error("leaf collinear triple");
   for(auto&t:tight)if(pc(chosen&t.mask)<t.lower)throw std::runtime_error("leaf capacity");
   ++total;bool ext=false;for(U128 cap:frozen_caps)if(!(chosen&~cap)){ext=true;break;}if(ext)++extendible;int above=0;for(int p=high(chosen)+1;p<P;++p)above+=!((anchor>>p)&1);if(above>=3)++least_eligible;if(masks_out)masks_out<<hex(chosen)<<"\n";return;
  }
  int row=-1,best=999;std::array<int,N>rank{5,4,6,3,7,2,8,1,9,0,10};
  for(int rr:rank)if(!(assigned&(1u<<rr))){int n=0;for(auto&p:patterns[rr])n+=compatible(p);if(n<best){best=n;row=rr;if(!n)break;}}
  if(best==0)return;
  U128 oldchosen=chosen,oldblocked=blocked;uint16_t oldassigned=assigned;auto oldcol=colcnt;
  for(auto&p:patterns[row])if(compatible(p)){
   U128 add=0,x=p.mask;bool self_secant=false;while(x){int q=low(x);x&=x-1;U128 y=chosen;while(y){int u=low(y);y&=y-1;U128 m=sec[q][u];if(m&(p.mask&~(U128(1)<<q)))self_secant=true;add|=m;}}
   // A two-point pattern lies in one as-yet-unassigned row, whereas every
   // chosen point lies in another row.  Hence a new point cannot lie on the
   // line through the other new point and a chosen point: that line would
   // meet the pattern row twice and therefore be that row.  Keep the general
   // test anyway, so a future change to the pattern decomposition stays safe.
   if(self_secant){++self_secant_rejects;continue;}
   if(p.b!=255)add|=sec[p.a][p.b];
   chosen|=p.mask;blocked|=add;assigned|=1u<<row;++colcnt[p.a%N];if(p.b!=255)++colcnt[p.b%N];
   if(feasible())dfs(depth+1);else{bool colbad=false;for(int c=0;c<N;++c){int av=0;for(int r=0;r<N;++r)if(!(assigned&(1u<<r))){int q=N*r+c;if(((residual>>q)&1)&&!((blocked>>q)&1))++av;}if(colcnt[c]+av<coltarget[c])colbad=true;}if(colbad)++col_rejects;else++line_rejects;}
   chosen=oldchosen;blocked=oldblocked;assigned=oldassigned;colcnt=oldcol;if(stopped)return;
  }
 }
 int run(){start=std::chrono::steady_clock::now();dfs(0);double s=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();std::cout<<(stopped?"INCOMPLETE":"COMPLETE")<<" count "<<dec(total)<<" least_eligible "<<dec(least_eligible);if(!frozen_caps.empty())std::cout<<" extendible "<<dec(extendible)<<" nonextendible "<<dec(total-extendible);std::cout<<" nodes "<<nodes<<" leaves "<<leaves<<" tight_lines "<<tight.size()<<" column_rejects "<<col_rejects<<" line_rejects "<<line_rejects<<" self_secant_rejects "<<self_secant_rejects<<" seconds "<<s<<"\n";return stopped?30:0;}
};
int main(int argc,char**argv)try{std::string ah,caps_path,output;int rp=-1,cp=-1;double t=30;for(int i=1;i<argc;++i){std::string a=argv[i];auto v=[&](){if(++i>=argc)throw std::runtime_error("arg");return std::string(argv[i]);};if(a=="--anchor")ah=v();else if(a=="--row-pair")rp=std::stoi(v());else if(a=="--col-pair")cp=std::stoi(v());else if(a=="--time")t=std::stod(v());else if(a=="--caps")caps_path=v();else if(a=="--output-masks")output=v();else throw std::runtime_error("unknown");}std::vector<U128>caps;if(!caps_path.empty()){std::ifstream f(caps_path);if(!f)throw std::runtime_error("open caps");std::string s;while(f>>s)caps.push_back(parse(s));if(caps.size()!=676)throw std::runtime_error("need 676 caps");}return Enum(parse(ah),rp,cp,t,std::move(caps),output).run();}catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<"\n";return 50;}
