// Exact exhaustive weak-admissibility search on the Fano incidence base.
// The accompanying symmetry certificate proves transitivity on all 168
// admissible single pairs, so fixing pair 0 loses no possible cardinality.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>
using U=std::uint64_t;
struct Edge {int a,b; U cells,opp; int rows,cols; std::vector<U> requirements;};
std::vector<Edge> edges;
U base=0;
std::array<int,16> chosen;
U crossmask[200][200]; bool crossactive[200][200];
std::array<unsigned long long,10> counts{};
unsigned long long trials=0;
std::vector<int> first_seven,first_eight;
int limit=8;
bool valid(int count,U occupied) {
    U all=occupied|base;
    for(int q=0;q<count;++q)
        for(U req:edges[chosen[q]].requirements)
            if((occupied&req)==req)return false;
    for(int q=0;q<count;++q)for(int r=0;r<q;++r){
        int a=chosen[q],b=chosen[r];
        if(crossactive[a][b] && (occupied&crossmask[a][b])==crossmask[a][b])return false;
    }
    int parent[16];for(int q=0;q<count;++q)parent[q]=q;
    auto find=[&](int x){while(parent[x]!=x)x=parent[x];return x;};
    for(int q=0;q<count;++q)for(int r=0;r<q;++r)
        if(edges[chosen[q]].opp==edges[chosen[r]].cells)parent[find(q)]=find(r);
    unsigned adjacency[16]={};int indegree[16]={};
    for(int q=0;q<count;++q){
        const auto &e=edges[chosen[q]];
        if((all&e.opp)!=e.opp)continue;
        for(int r=0;r<count;++r)if(q!=r && (e.opp&edges[chosen[r]].cells)){
            int a=find(q),b=find(r);
            if(a!=b)adjacency[a]|=1u<<b;
        }
    }
    for(int q=0;q<count;++q)for(int r=0;r<count;++r)
        if(adjacency[q]>>r&1)indegree[r]++;
    int seen=0;bool removed[16]={};
    for(int iter=0;iter<count;++iter){
        int q=-1;for(int j=0;j<count;++j)if(!removed[j] && !indegree[j]){q=j;break;}
        if(q<0)break;
        removed[q]=true;seen++;
        for(int r=0;r<count;++r)if(adjacency[q]>>r&1)indegree[r]--;
    }
    return seen==count;
}
void search(int next,int depth,U occupied) {
    counts[depth]++;
    if(depth==7 && first_seven.empty()) {
        first_seven.assign(chosen.begin(),chosen.begin()+7);
        std::cerr<<"Found weak total 28 after "<<trials<<" candidate extensions\n";
    }
    if(depth==8) {
        if(first_eight.empty())first_eight.assign(chosen.begin(),chosen.begin()+8);
        return;
    }
    if(depth>=limit)return;
    for(int i=next;i<(int)edges.size();++i){
        if(edges[i].cells&occupied)continue;
        chosen[depth]=i;trials++;
        if(valid(depth+1,occupied|edges[i].cells))search(i+1,depth+1,occupied|edges[i].cells);
    }
}
int main(int argc,char**argv) {
    for(int r=0;r<7;++r)for(int d:{0,1,3})base|=U(1)<<(r*7+(r+d)%7);
    for(int a=0;a<49;++a)if(!(base>>a&1))
        for(int b=a+1;b<49;++b)if(!(base>>b&1)) {
            Edge e{a,b,(U(1)<<a)|(U(1)<<b),0,(1<<(a/7))|(1<<(b/7)),(1<<(a%7))|(1<<(b%7)),{}};
            if(a/7!=b/7 && a%7!=b%7){
                e.opp=(U(1)<<(a/7*7+b%7))|(U(1)<<(b/7*7+a%7));
                if((e.opp&base)==e.opp)continue;
            }
            bool ok=true;
            for(int c=0;c<49;++c)if(base>>c&1) {
                if((e.rows>>(c/7)&1)||(e.cols>>(c%7)&1))continue;
                U mask=0;
                for(int r=0;r<7;++r)if(e.rows>>r&1)mask|=U(1)<<(r*7+c%7);
                for(int j=0;j<7;++j)if(e.cols>>j&1)mask|=U(1)<<(c/7*7+j);
                mask&=~base;
                if((mask&e.cells)==mask){ok=false;break;}
                e.requirements.push_back(mask);
            }
            if(ok)edges.push_back(e);
        }
    if(edges.size()!=168){std::cerr<<"Unexpected single-pair count\n";return 2;}
    for(int i=0;i<168;++i)for(int j=0;j<168;++j){
        auto &a=edges[i];auto &b=edges[j];
        crossactive[i][j]=!(a.rows&b.rows)&&!(a.cols&b.cols);
        if(crossactive[i][j]){
            U mask=0;
            for(int r=0;r<7;++r)for(int c=0;c<7;++c)
                if(((a.rows>>r&1)&&(b.cols>>c&1))||((b.rows>>r&1)&&(a.cols>>c&1)))
                    mask|=U(1)<<(r*7+c);
            crossmask[i][j]=mask&~base;
        }
    }
    // Optional input file: one line per matching, k followed by 2*k cell IDs.
    // This mode cross-checks the C++ predicate against the Python implementation.
    if(argc==3 && std::string(argv[1])=="--check") {
        std::ifstream in(argv[2]);int k,a,b;
        while(in>>k){
            U occupied=0;bool found=true;
            for(int q=0;q<k;++q){
                in>>a>>b;if(a>b)std::swap(a,b);
                int idx=-1;for(int i=0;i<168;++i)if(edges[i].a==a&&edges[i].b==b)idx=i;
                if(idx<0 || (occupied&((U(1)<<a)|(U(1)<<b))))found=false;
                chosen[q]=idx<0?0:idx;occupied|=(U(1)<<a)|(U(1)<<b);
            }
            std::cout<<(found&&valid(k,occupied)?1:0)<<"\n";
        }
        return 0;
    }
    chosen[0]=0;
    search(1,1,edges[0].cells);
    std::cout<<"{\n\"single_pairs\":168,\n\"normalized_pair\":["<<edges[0].a<<","<<edges[0].b<<"],\n";
    std::cout<<"\"fixed_pair_accepted_prefix_counts\":[";
    for(int i=0;i<=8;++i){if(i)std::cout<<",";std::cout<<counts[i];}
    std::cout<<"],\n\"predicate_calls\":"<<trials<<",\n\"first_seven\":[";
    for(unsigned i=0;i<first_seven.size();++i){
        if(i)std::cout<<",";
        const auto&e=edges[first_seven[i]];std::cout<<"["<<e.a<<","<<e.b<<"]";
    }
    std::cout<<"],\n\"total29_exists\":"<<(first_eight.empty()?"false":"true")<<"\n}\n";
    return 0;
}
