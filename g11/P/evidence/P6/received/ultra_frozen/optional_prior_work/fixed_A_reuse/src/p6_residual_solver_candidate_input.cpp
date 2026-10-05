// Exact P6 residual solver after a fixed unordered pair of size-21 caps.
// Residual profile: (20,20,20,19). Enumerate complete size-20 caps,
// choose the first two in numeric mask order, then solve the remaining
// 39 points as an exact 20/19 Boolean cap partition with the third size-20
// mask required to exceed the second. Exit: 10 SAT, 20 exhaustive UNSAT,
// 30 resource-limited INCOMPLETE, 2 input/internal error.

#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

__extension__ typedef unsigned __int128 U128;
static constexpr int N = 11, P = 121;
static constexpr U128 FULL = (U128{1} << P) - 1;

struct Line { U128 mask=0; uint8_t length=0; };
struct Candidate { U128 mask=0; uint16_t singleton_rows=0, singleton_cols=0; };
struct RowOption { U128 mask=0; std::array<U128,P> block_against{}; uint8_t c1=0,c2=0,n=0; };
struct CriticalLine { U128 mask=0; uint8_t lower=0; };
struct BinaryConstraint { std::array<uint8_t,4> vars{}; uint8_t length=0; };
enum class Result { SAT, UNSAT, INCOMPLETE };

static int pc(U128 x) { return std::popcount((uint64_t)x)+std::popcount((uint64_t)(x>>64)); }
static int least(U128 x) { uint64_t lo=(uint64_t)x; return lo?std::countr_zero(lo):64+std::countr_zero((uint64_t)(x>>64)); }
static std::string hex31(U128 x){ static const char*d="0123456789abcdef"; std::string s(31,'0'); for(int i=30;i>=0;--i){s[i]=d[(unsigned)(x&15)];x>>=4;}return s; }
static U128 parse_hex31(const std::string& s){
  if(s.size()!=31) throw std::runtime_error("candidate mask width");
  U128 x=0; for(char c:s){x<<=4;if(c>='0'&&c<='9')x|=c-'0';else if(c>='a'&&c<='f')x|=c-'a'+10;else throw std::runtime_error("candidate mask hex");}
  if(x>>121) throw std::runtime_error("candidate high bits");
  return x;
}

static std::vector<Line> make_lines(){
  std::vector<Line> v;
  for(int dc=0;dc<N;++dc) for(int dr=-(N-1);dr<N;++dr){
    if(dc==0){if(dr!=1)continue;} else if(std::gcd(dc,std::abs(dr))!=1) continue;
    for(int r=0;r<N;++r) for(int c=0;c<N;++c){
      if(0<=r-dr&&r-dr<N&&0<=c-dc&&c-dc<N) continue;
      U128 m=0; int rr=r,cc=c;
      while(0<=rr&&rr<N&&0<=cc&&cc<N){m|=U128{1}<<(rr*N+cc);rr+=dr;cc+=dc;}
      int z=pc(m); if(z>=3)v.push_back({m,(uint8_t)z});
    }
  }
  std::sort(v.begin(),v.end(),[](auto&a,auto&b){return a.mask<b.mask;});
  if(v.size()!=628||std::adjacent_find(v.begin(),v.end(),[](auto&a,auto&b){return a.mask==b.mask;})!=v.end()) throw std::runtime_error("geometry");
  return v;
}

class Solver{
 public:
  Solver(std::string pair_path,std::string out_path,std::string candidate_path,
         std::string candidate_input_path,uint64_t node_limit,double sec_limit,bool candidate_only)
    : lines_(make_lines()), out_path_(std::move(out_path)),
      candidate_path_(std::move(candidate_path)), candidate_input_path_(std::move(candidate_input_path)), node_limit_(node_limit),
      sec_limit_(sec_limit), candidate_only_(candidate_only){
    build_geometry(); read_pair(pair_path); prepare();
  }

  int run(){
    started_=std::chrono::steady_clock::now();
    Result r=candidate_input_path_.empty()?generate_candidates():load_candidates();
    candidate_seconds_=elapsed();
    if(r==Result::UNSAT) dump_candidates();
    if(r==Result::UNSAT && candidate_only_){
      double sec=elapsed();
      std::cout<<"AUX_P6_CANDIDATE_ENUM_COMPLETE"
        <<" candidate_nodes "<<candidate_nodes_
        <<" candidate_leaves "<<candidate_leaves_
        <<" candidates "<<candidates_.size()
        <<" first_capacity_rejects "<<first_capacity_rejects_
        <<" work_nodes "<<work_nodes_
        <<" seconds "<<sec<<"\n";
      return 40;
    }
    if(r==Result::UNSAT) r=search_pairs();
    double sec=elapsed();
    const char* status=r==Result::SAT?"SAT_P6_RESIDUAL":r==Result::UNSAT?"UNSAT_P6_RESIDUAL":"INCOMPLETE_P6_RESIDUAL";
    std::cout<<status
      <<" candidate_nodes "<<candidate_nodes_
      <<" candidate_leaves "<<candidate_leaves_
      <<" candidates "<<candidates_.size()
      <<" first_capacity_rejects "<<first_capacity_rejects_
      <<" pair_tests "<<pair_tests_
      <<" pair_overlap_rejects "<<pair_overlap_rejects_
      <<" pair_singleton_rejects "<<pair_singleton_rejects_
      <<" pair_capacity_rejects "<<pair_capacity_rejects_
      <<" pair_survivors "<<pair_survivors_
      <<" binary_instances "<<binary_instances_
      <<" binary_nodes "<<binary_nodes_
      <<" binary_conflicts "<<binary_conflicts_
      <<" binary_leaves "<<binary_leaves_
      <<" order_rejects "<<order_rejects_
      <<" work_nodes "<<work_nodes_
      <<" candidate_seconds "<<candidate_seconds_
      <<" post_candidate_seconds "<<(sec-candidate_seconds_)
      <<" seconds "<<sec<<"\n";
    if(r==Result::SAT){ validate_solution(); write_solution(); print_masks(); return 10; }
    return r==Result::UNSAT?20:30;
  }

 private:
  double elapsed()const{return std::chrono::duration<double>(std::chrono::steady_clock::now()-started_).count();}
  bool consume(){
    if(node_limit_&&work_nodes_>=node_limit_){limited_=true;return false;}
    if(sec_limit_>0 && (work_nodes_&0x3fff)==0 && elapsed()>=sec_limit_){limited_=true;return false;}
    ++work_nodes_; return true;
  }
  void build_geometry(){
    for(size_t i=0;i<lines_.size();++i){U128 s=lines_[i].mask;while(s){int p=least(s);inc_[p].push_back(i);s&=s-1;}}
    for(int a=0;a<P;++a){int ar=a/N,ac=a%N;for(int b=a+1;b<P;++b){int br=b/N,bc=b%N;U128 m=0;for(int c=0;c<P;++c){int cr=c/N,cc=c%N;if((br-ar)*(cc-ac)==(bc-ac)*(cr-ar))m|=U128{1}<<c;}pair_line_[a][b]=pair_line_[b][a]=m;}}
    for(int r=0;r<N;++r)for(int c=0;c<N;++c){int p=r*N+c;row_masks_[r]|=U128{1}<<p;col_masks_[c]|=U128{1}<<p;}
    for(int i=0;i<N;++i){main_diag_|=U128{1}<<(i*N+i);anti_diag_|=U128{1}<<(i*N+10-i);}
  }
  static std::pair<uint16_t,uint16_t> singleton_masks(U128 m,int deficit){
    uint16_t rs=0,cs=0;U128 shortrow=(U128{1}<<N)-1;
    for(int r=0;r<N;++r){int n=pc((m>>(r*N))&shortrow);if(n==1)rs|=uint16_t{1}<<r;else if(n!=2)throw std::runtime_error("row multiplicity");}
    for(int c=0;c<N;++c){int n=0;for(int r=0;r<N;++r)n+=(m>>(r*N+c))&1;if(n==1)cs|=uint16_t{1}<<c;else if(n!=2)throw std::runtime_error("col multiplicity");}
    if(std::popcount(rs)!=deficit||std::popcount(cs)!=deficit){
      throw std::runtime_error("singleton deficit");
    }
    return {rs,cs};
  }
  void read_pair(const std::string& path){
    std::ifstream f(path);if(!f)throw std::runtime_error("cannot open pair");
    for(int p=0;p<P;++p){int x;if(!(f>>x))throw std::runtime_error("short pair");if(x==1)a_|=U128{1}<<p;else if(x==2)b_|=U128{1}<<p;else if(x!=0)throw std::runtime_error("pair value");}
    int extra;if(f>>extra)throw std::runtime_error("extra pair value");
    if(pc(a_)!=21||pc(b_)!=21||(a_&b_))throw std::runtime_error("pair profile");
    for(U128 m:{a_,b_})for(auto&l:lines_)if(pc(m&l.mask)>2)throw std::runtime_error("fixed class not cap");
    residual_=FULL^a_^b_;if(pc(residual_)!=79)throw std::runtime_error("residual size");
    auto sa=singleton_masks(a_,1),sb=singleton_masks(b_,1);
    fixed_single_rows_=sa.first|sb.first;fixed_single_cols_=sa.second|sb.second;
    if(std::popcount(fixed_single_rows_)!=2||std::popcount(fixed_single_cols_)!=2)throw std::runtime_error("fixed singleton collision");
  }
  void prepare(){
    eligible_single_rows_=0;
    for(int r=0;r<N;++r){int n=0;for(int c=0;c<N;++c)n+=(residual_>>(r*N+c))&1;if(n==7)eligible_single_rows_|=uint16_t{1}<<r;else if(n!=8)throw std::runtime_error("residual row length");}
    uint16_t eligible_cols=0;
    for(int c=0;c<N;++c){int n=0;for(int r=0;r<N;++r)n+=(residual_>>(r*N+c))&1;if(n==7)eligible_cols|=uint16_t{1}<<c;else if(n!=8)throw std::runtime_error("residual col length");}
    if(std::popcount(eligible_single_rows_)!=9||std::popcount(eligible_cols)!=9)throw std::runtime_error("residual 8/7 profile");
    if((eligible_single_rows_|fixed_single_rows_)!=((uint16_t{1}<<N)-1) || (eligible_cols|fixed_single_cols_)!=((uint16_t{1}<<N)-1)) throw std::runtime_error("singleton partition basis");
    for(int r=0;r<N;++r){
      U128 m=residual_&row_masks_[r];std::array<int,N> pts{};int np=0;while(m){pts[np++]=least(m);m&=m-1;}
      for(int i=0;i<np;++i){RowOption o;o.mask=U128{1}<<pts[i];o.c1=pts[i]%N;o.n=1;for(int old=0;old<P;++old)o.block_against[old]=pair_line_[pts[i]][old];row_opts1_[r].push_back(std::move(o));}
      for(int i=0;i<np;++i)for(int j=i+1;j<np;++j){RowOption o;o.mask=(U128{1}<<pts[i])|(U128{1}<<pts[j]);o.c1=pts[i]%N;o.c2=pts[j]%N;o.n=2;for(int old=0;old<P;++old)o.block_against[old]=pair_line_[pts[i]][old]|pair_line_[pts[j]][old];row_opts2_[r].push_back(std::move(o));}
    }
    for(int row=N;row>=0;--row)for(int c=0;c<N;++c){
      future_col_masks_[row][c]=row==N?0:future_col_masks_[row+1][c]|(residual_&row_masks_[row]&col_masks_[c]);
    }
    for(int row=N;row>=0;--row)future_point_masks_[row]=row==N?0:future_point_masks_[row+1]|(residual_&row_masks_[row]);
    first_critical_.clear();pair_critical_.clear();
    for(auto&l:lines_){U128 m=residual_&l.mask;int z=pc(m);if(z>8)throw std::runtime_error("four-cap capacity");if(z>6)first_critical_.push_back({m,(uint8_t)(z-6)});if(z>4)pair_critical_.push_back({m,(uint8_t)(z-4)});}
  }
  bool meets_diags(U128 m)const{return(m&main_diag_)&&(m&anti_diag_);}
  Result generate_candidates(){
    candidates_.clear();
    for(int r1=0;r1<N;++r1)if((eligible_single_rows_>>r1)&1)for(int r2=r1+1;r2<N;++r2)if((eligible_single_rows_>>r2)&1){
      single_r1_=r1;single_r2_=r2;coldeg_.fill(0);selected_count_=0;Result z=cap_recurse(0,0,0);if(z==Result::INCOMPLETE)return z;
    }
    std::sort(candidates_.begin(),candidates_.end(),[](auto&a,auto&b){return a.mask<b.mask;});
    auto dup=std::adjacent_find(candidates_.begin(),candidates_.end(),[](auto&a,auto&b){return a.mask==b.mask;});if(dup!=candidates_.end())throw std::runtime_error("duplicate candidate");
    return Result::UNSAT;
  }
  bool column_profile_feasible(int row,U128 blocked)const{
    int forced_single=0,potential_single=0;U128 free_mask=~blocked;
    for(int c=0;c<N;++c){
      int d=coldeg_[c];U128 a=future_col_masks_[row][c]&free_mask;
      bool one=a!=0,two=(a&(a-1))!=0;
      if((fixed_single_cols_>>c)&1){
        if(d==0&&!two)return false;
        if(d==1&&!one)return false;
      }else{
        if(d<2)++potential_single;
        if(d==0){if(!one)return false;if(!two)++forced_single;}
        else if(d==1&&!one)++forced_single;
      }
    }
    return forced_single<=2&&potential_single>=2;
  }
  Result cap_recurse(int row,U128 selected,U128 blocked){
    if(!consume()) return Result::INCOMPLETE;
    ++candidate_nodes_;
    if(!column_profile_feasible(row,blocked))return Result::UNSAT;
    if(row==N){
      ++candidate_leaves_;uint16_t cols=0;for(int c=0;c<N;++c){if(coldeg_[c]==1)cols|=uint16_t{1}<<c;else if(coldeg_[c]!=2)return Result::UNSAT;}
      if(std::popcount(cols)!=2||(cols&fixed_single_cols_)||!meets_diags(selected))return Result::UNSAT;
      for(auto&cl:first_critical_)if(pc(selected&cl.mask)<cl.lower){++first_capacity_rejects_;return Result::UNSAT;}
      uint16_t rows=(uint16_t{1}<<single_r1_)|(uint16_t{1}<<single_r2_);
      candidates_.push_back({selected,rows,cols});return Result::UNSAT;
    }
    int need=(row==single_r1_||row==single_r2_)?1:2;
    const auto&opts=need==1?row_opts1_[row]:row_opts2_[row];
    for(const auto&o:opts){
      if(o.mask&blocked||coldeg_[o.c1]>=2||(o.n==2&&coldeg_[o.c2]>=2))continue;
      U128 nb=blocked;for(int k=0;k<selected_count_;++k)nb|=o.block_against[selected_points_[k]];
      U128 t=o.mask;while(t){int p=least(t);selected_points_[selected_count_++]=p;t&=t-1;}
      ++coldeg_[o.c1];if(o.n==2)++coldeg_[o.c2];
      Result z=cap_recurse(row+1,selected|o.mask,nb);
      if(o.n==2){--coldeg_[o.c2];}--coldeg_[o.c1];selected_count_-=o.n;
      if(z==Result::INCOMPLETE)return z;
    }
    return Result::UNSAT;
  }
  Result search_pairs(){
    for(size_t i=0;i<candidates_.size();++i)for(size_t j=i+1;j<candidates_.size();++j){
      if(!consume()) return Result::INCOMPLETE;
      ++pair_tests_;
      auto& a=candidates_[i];
      auto& b=candidates_[j];
      if(a.mask&b.mask){++pair_overlap_rejects_;continue;}
      if((a.singleton_rows&b.singleton_rows)||(a.singleton_cols&b.singleton_cols)){++pair_singleton_rejects_;continue;}
      U128 selected=a.mask|b.mask;bool ok=true;for(auto&cl:pair_critical_)if(pc(selected&cl.mask)<cl.lower){ok=false;break;}if(!ok){++pair_capacity_rejects_;continue;}
      ++pair_survivors_;
      third_min_mask_=b.mask;
      U128 r39=residual_^selected;
      Result z=solve_binary(r39);
      if(z==Result::INCOMPLETE) return z;
      if(z==Result::SAT){
        c_=a.mask;
        d_=b.mask;
        e_=binary_one_;
        f_=r39^binary_one_;
        return z;
      }
    }
    return Result::UNSAT;
  }
  Result solve_binary(U128 points){
    ++binary_instances_;local_id_.fill(-1);binary_n_=0;U128 s=points;while(s){int p=least(s);local_id_[p]=binary_n_;global_point_[binary_n_++]=p;s&=s-1;}if(binary_n_!=39)throw std::runtime_error("binary size");
    binary_constraints_n_=0;binary_degree_.fill(0);
    for(auto&l:lines_){U128 m=points&l.mask;int z=pc(m);if(z>4)throw std::runtime_error("pair capacity inconsistency");if(z<3)continue;BinaryConstraint bc;bc.length=z;int k=0;while(m){int p=least(m),id=local_id_[p];bc.vars[k++]=id;++binary_degree_[id];m&=m-1;}binary_constraints_[binary_constraints_n_++]=bc;}
    std::array<int8_t,39>a;a.fill(-1);return binary_recurse(a);
  }
  bool binary_propagate(std::array<int8_t,39>&a){
    for(;;){bool changed=false;int ones=0,unk=0;for(int i=0;i<binary_n_;++i){ones+=a[i]==1;unk+=a[i]<0;}if(ones>20||ones+unk<20)return false;if(ones==20||ones+unk==20){int force=ones==20?0:1;for(int i=0;i<binary_n_;++i)if(a[i]<0)a[i]=force,changed=true;}
      for(int i=0;i<binary_constraints_n_;++i){auto&c=binary_constraints_[i];int o=0,u=0;for(int j=0;j<c.length;++j){int v=a[c.vars[j]];o+=v==1;u+=v<0;}int lower=c.length-2;if(o>2||o+u<lower)return false;if(o==2||o+u==lower){int force=o==2?0:1;for(int j=0;j<c.length;++j){auto&v=a[c.vars[j]];if(v<0)v=force,changed=true;}}}
      if(!changed)return true;
    }
  }
  Result binary_recurse(std::array<int8_t,39>a){
    if(!consume()) return Result::INCOMPLETE;
    ++binary_nodes_;
    if(!binary_propagate(a)){
      ++binary_conflicts_;
      return Result::UNSAT;
    }
    int chosen=-1,best=-1,ones=0;for(int i=0;i<binary_n_;++i){ones+=a[i]==1;if(a[i]<0&&binary_degree_[i]>best)best=binary_degree_[i],chosen=i;}
    if(chosen<0){++binary_leaves_;U128 m=0;for(int i=0;i<binary_n_;++i)if(a[i]==1)m|=U128{1}<<global_point_[i];if(m<=third_min_mask_){++order_rejects_;return Result::UNSAT;}binary_one_=m;return Result::SAT;}
    int pref=ones<10?1:0;for(int v:{pref,1-pref}){auto child=a;child[chosen]=v;Result z=binary_recurse(child);if(z!=Result::UNSAT)return z;}return Result::UNSAT;
  }

  Result load_candidates(){
    std::ifstream f(candidate_input_path_); if(!f) throw std::runtime_error("cannot open candidate input");
    std::string header; if(!std::getline(f,header)||header!="mask\tsingleton_rows\tsingleton_cols") throw std::runtime_error("candidate header");
    candidates_.clear(); std::string mask_s; unsigned long sr=0,sc=0;
    while(f>>mask_s>>sr>>sc){
      U128 m=parse_hex31(mask_s); if(pc(m)!=20||(m&~residual_)) throw std::runtime_error("candidate mask/profile");
      for(const auto& l:lines_) if(pc(m&l.mask)>2) throw std::runtime_error("candidate not cap");
      auto sm=singleton_masks(m,2); if(sm.first!=sr||sm.second!=sc) throw std::runtime_error("candidate singleton metadata");
      if((sm.first&fixed_single_rows_)||(sm.second&fixed_single_cols_)) throw std::runtime_error("candidate singleton collision");
      if(!meets_diags(m)) throw std::runtime_error("candidate diagonal condition");
      for(const auto& cl:first_critical_) if(pc(m&cl.mask)<cl.lower) throw std::runtime_error("candidate capacity condition");
      candidates_.push_back({m,(uint16_t)sr,(uint16_t)sc});
    }
    if(!f.eof()) throw std::runtime_error("candidate parse failure");
    if(!std::is_sorted(candidates_.begin(),candidates_.end(),[](auto&a,auto&b){return a.mask<b.mask;})) throw std::runtime_error("candidate order");
    if(std::adjacent_find(candidates_.begin(),candidates_.end(),[](auto&a,auto&b){return a.mask==b.mask;})!=candidates_.end()) throw std::runtime_error("duplicate candidate input");
    return Result::UNSAT;
  }

  void dump_candidates()const{
    if(candidate_path_.empty()) return;
    const std::string partial=candidate_path_+".partial";
    std::ofstream o(partial);
    if(!o) throw std::runtime_error("cannot write candidate ledger");
    o<<"mask\tsingleton_rows\tsingleton_cols\n";
    for(const auto& c:candidates_){
      o<<hex31(c.mask)<<'\t'<<c.singleton_rows<<'\t'<<c.singleton_cols<<'\n';
    }
    o.close();
    if(!o) throw std::runtime_error("candidate ledger write failure");
    if(std::rename(partial.c_str(),candidate_path_.c_str())!=0){
      throw std::runtime_error("candidate ledger rename failure");
    }
  }

  void validate_solution()const{
    std::array<U128,6>x{a_,b_,c_,d_,e_,f_};std::array<int,6>sz{21,21,20,20,20,19};U128 u=0;
    for(int i=0;i<6;++i){if(pc(x[i])!=sz[i])throw std::runtime_error("witness size");if(u&x[i])throw std::runtime_error("witness overlap");u|=x[i];for(auto&l:lines_)if(pc(x[i]&l.mask)>2)throw std::runtime_error("witness triple");}
    if(u!=FULL) throw std::runtime_error("witness cover");
    if(!(c_<d_&&d_<e_)) throw std::runtime_error("size20 order");
  }
  void write_solution()const{if(out_path_.empty())return;std::ofstream o(out_path_);if(!o)throw std::runtime_error("cannot write witness");std::array<U128,6>x{a_,b_,c_,d_,e_,f_};for(int r=0;r<N;++r){for(int c=0;c<N;++c){int p=r*N+c,col=-1;for(int k=0;k<6;++k)if((x[k]>>p)&1){col=k+1;break;}if(c)o<<' ';o<<col;}o<<'\n';}}
  void print_masks()const{std::cerr<<"witness_masks A="<<hex31(a_)<<" B="<<hex31(b_)<<" C="<<hex31(c_)<<" D="<<hex31(d_)<<" E="<<hex31(e_)<<" F="<<hex31(f_)<<"\n";}

  std::vector<Line> lines_;std::array<std::vector<size_t>,P>inc_{};std::array<std::array<U128,P>,P>pair_line_{};
  std::array<U128,N>row_masks_{},col_masks_{};std::array<std::array<U128,N>,N+1>future_col_masks_{};std::array<U128,N+1>future_point_masks_{};
  std::array<std::vector<RowOption>,N>row_opts1_{},row_opts2_{};
  U128 a_=0,b_=0,residual_=0,main_diag_=0,anti_diag_=0,c_=0,d_=0,e_=0,f_=0,binary_one_=0,third_min_mask_=0;
  uint16_t fixed_single_rows_=0,fixed_single_cols_=0,eligible_single_rows_=0;std::vector<CriticalLine>first_critical_,pair_critical_;std::vector<Candidate>candidates_;
  int single_r1_=0,single_r2_=0,selected_count_=0;std::array<uint8_t,N>coldeg_{};std::array<int,20>selected_points_{};
  std::array<int8_t,P>local_id_{};std::array<int,39>global_point_{};std::array<uint8_t,39>binary_degree_{};std::array<BinaryConstraint,628>binary_constraints_{};int binary_n_=0,binary_constraints_n_=0;
  std::string out_path_,candidate_path_,candidate_input_path_;uint64_t node_limit_=0,work_nodes_=0;double sec_limit_=0,candidate_seconds_=0;bool limited_=false,candidate_only_=false;std::chrono::steady_clock::time_point started_;
  uint64_t candidate_nodes_=0,candidate_leaves_=0,first_capacity_rejects_=0,pair_tests_=0,pair_overlap_rejects_=0,pair_singleton_rejects_=0,pair_capacity_rejects_=0,pair_survivors_=0,binary_instances_=0,binary_nodes_=0,binary_conflicts_=0,binary_leaves_=0,order_rejects_=0;
};

int main(int argc,char**argv){
  try{std::string pair,out="p6_witness.grid",candidate_path,candidate_input_path;uint64_t nodes=0;double seconds=0;bool candidate_only=false;for(int i=1;i<argc;++i){std::string a=argv[i];auto need=[&](){if(++i>=argc)throw std::runtime_error("missing argument");return std::string(argv[i]);};if(a=="--pair")pair=need();else if(a=="--out")out=need();else if(a=="--dump-candidates")candidate_path=need();else if(a=="--load-candidates")candidate_input_path=need();else if(a=="--candidate-only")candidate_only=true;else if(a=="--node-limit")nodes=std::stoull(need());else if(a=="--seconds")seconds=std::stod(need());else throw std::runtime_error("bad arg "+a);}if(pair.empty())throw std::runtime_error("--pair required");Solver s(pair,out,candidate_path,candidate_input_path,nodes,seconds,candidate_only);return s.run();}
  catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<"\n";return 2;}
}
