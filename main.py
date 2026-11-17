import csv, math, tkinter as tk
from pathlib import Path
from tkinter import messagebox

BASE=Path(__file__).resolve().parent
DATA=BASE/"Geumjeong_Student_Package"/"Geumjeong_Student_Package"/"geumjeong_apt_2023_2025_ml.csv"
NAVY,BLUE,BG,PALE="#123d68","#2878d0","#f4f7fb","#e8f2ff"
def num(v):
    try:return float(str(v).replace(",","").replace("㎡","").replace("m²","").strip())
    except (ValueError,TypeError):return None
def load():
    if not DATA.exists():raise FileNotFoundError(f"CSV 파일이 없습니다.\n{DATA}")
    rows=None
    for enc in ("utf-8-sig","cp949","utf-8"):
        try:
            with DATA.open(encoding=enc,newline="") as f:rows=list(csv.DictReader(f))
            break
        except UnicodeDecodeError:pass
    if not rows:raise ValueError("CSV 데이터가 비어 있습니다.")
    headers=list(rows[0])
    def col(keys):
        for key in keys:
            for name in headers:
                if key.casefold() in name.casefold():return name
    ac=col(("전용면적","exclusive_area","area","면적"))
    pc=col(("거래금액","매매가","매매가격","transaction_amount","price","금액"))
    if not ac or not pc:raise ValueError("전용면적/거래가격 열을 찾지 못했습니다.\n"+", ".join(headers))
    pairs=[(num(r.get(ac)),num(r.get(pc))) for r in rows]
    pairs=[(x,y) for x,y in pairs if x is not None and y is not None and x>0 and y>=0]
    if len(pairs)<3:raise ValueError("유효한 거래 데이터가 부족합니다.")
    return pairs
def model(pairs):
    ps=sorted(pairs,key=lambda p:((int(p[0]*1009)+int(p[1])*9176)%100003,p[0]))
    n=max(2,min(len(ps)-1,int(len(ps)*.8))); tr,te=ps[:n],ps[n:]
    mx=sum(x for x,y in tr)/len(tr);my=sum(y for x,y in tr)/len(tr)
    den=sum((x-mx)**2 for x,y in tr)
    if not den:raise ValueError("면적 값이 모두 같아 회귀 모델을 만들 수 없습니다.")
    a=sum((x-mx)*(y-my) for x,y in tr)/den;b=my-a*mx
    es=[b+a*x-y for x,y in te];mae=sum(abs(e) for e in es)/len(es);rmse=math.sqrt(sum(e*e for e in es)/len(es))
    avg=sum(y for x,y in te)/len(te);tot=sum((y-avg)**2 for x,y in te)
    return a,b,tr,mae,rmse,1-sum(e*e for e in es)/tot if tot else 0
class App(tk.Tk):
    def __init__(self):
        super().__init__();self.title("아파트 매매가격 예측 프로그램");self.geometry("1280x760");self.minsize(980,650);self.configure(bg=BG)
        self.pairs=load();self.a,self.b,self.train,self.mae,self.rmse,self.r2=model(self.pairs);self.pred=None;self.ui();self.predict()
    def ui(self):
        hd=tk.Frame(self,bg=NAVY,padx=28,pady=16);hd.pack(fill="x",padx=18,pady=(16,12))
        tk.Label(hd,text="아파트 매매가격 예측 프로그램",font=("맑은 고딕",22,"bold"),bg=NAVY,fg="white").pack(anchor="w")
        tk.Label(hd,text="부산광역시 금정구 · 계약기간 2023–2025년 · 전용면적 1개 변수",font=("맑은 고딕",11),bg=NAVY,fg="#d8e8fa").pack(anchor="w")
        body=tk.Frame(self,bg=BG);body.pack(fill="both",expand=True,padx=22,pady=(0,18))
        l=tk.Frame(body,bg="white",highlightbackground="#d5e1ef",highlightthickness=1,padx=24,pady=20,width=370);l.pack(side="left",fill="y",padx=(0,16));l.pack_propagate(False)
        r=tk.Frame(body,bg="white",highlightbackground="#d5e1ef",highlightthickness=1,padx=20,pady=18);r.pack(side="left",fill="both",expand=True)
        tk.Label(l,text="전용면적 기반 가격 예측",font=("맑은 고딕",17,"bold"),bg="white",fg="#182b45").pack(anchor="w",pady=(2,16))
        tk.Label(l,text="전용면적 (m²)",font=("맑은 고딕",12),bg="white",fg="#58708f").pack(anchor="w")
        self.area=tk.StringVar(value="84.0");tk.Entry(l,textvariable=self.area,font=("맑은 고딕",20,"bold"),bg="#f7f9fc",relief="solid",bd=1).pack(fill="x",ipady=9,pady=(7,13))
        tk.Button(l,text="가격 예측하기",command=self.predict,font=("맑은 고딕",15,"bold"),bg=BLUE,fg="white",relief="flat",pady=10).pack(fill="x")
        card=tk.Frame(l,bg=PALE,padx=16,pady=12);card.pack(fill="x",pady=(19,17))
        tk.Label(card,text="예상 매매가격 (모델 예측)",font=("맑은 고딕",11),bg=PALE,fg="#285a8b").pack(anchor="w")
        self.result=tk.Label(card,text="—",font=("맑은 고딕",22,"bold"),bg=PALE,fg="#0d477e");self.result.pack(anchor="w")
        self.basis=tk.Label(card,text="",font=("맑은 고딕",10),bg=PALE,fg="#58708f");self.basis.pack(anchor="w")
        tk.Label(l,text="테스트 데이터 모델 성능",font=("맑은 고딕",14,"bold"),bg="white").pack(anchor="w",pady=(5,7))
        for name,val in (("MAE",self.mae),("RMSE",self.rmse),("R²",self.r2)):
            row=tk.Frame(l,bg="white");row.pack(fill="x",pady=4);tk.Label(row,text=name,bg="white",fg="#58708f",font=("맑은 고딕",12)).pack(side="left",padx=8)
            tk.Label(row,text=f"{val:,.0f} 만원" if name!="R²" else f"{val:.3f}",bg="white",font=("맑은 고딕",12,"bold")).pack(side="right",padx=8)
        tk.Label(r,text="전용면적과 매매가격의 관계",font=("맑은 고딕",17,"bold"),bg="white").pack(anchor="w")
        tk.Label(r,text="학습 데이터 산점도 + 단순 선형회귀 예측선",font=("맑은 고딕",11),bg="white",fg="#58708f").pack(anchor="w",pady=(2,6))
        self.chart=tk.Canvas(r,bg="white",highlightthickness=0);self.chart.pack(fill="both",expand=True);self.chart.bind("<Configure>",lambda e:self.draw())
        tk.Label(r,text="※ CSV를 80:20으로 분할해 학습합니다. 가격 단위는 CSV 기준입니다.\n※ 면적만으로 예측하므로 실제 개별 주택 가격을 보장하지 않습니다.",font=("맑은 고딕",9),bg="white",fg="#6782a3",justify="left").pack(anchor="w",pady=(6,0))
    def predict(self):
        try:
            x=float(self.area.get().replace(",","").strip())
            if not math.isfinite(x) or x<=0:raise ValueError
        except ValueError:messagebox.showerror("입력 오류","전용면적은 0보다 큰 숫자로 입력해 주세요.");return
        self.pred=self.b+self.a*x;self.result.config(text=f"{self.pred:,.0f} 만원");self.basis.config(text=f"전용면적 {x:g} m² 기준");self.draw()
    def draw(self):
        if not hasattr(self,"chart"):return
        c=self.chart;c.delete("all");w,h=c.winfo_width(),c.winfo_height()
        if w<200 or h<160:return
        l,r,t,bt=58,w-18,15,h-42;xs=[p[0] for p in self.pairs];ys=[p[1] for p in self.pairs]
        xmin,xmax=min(xs),max(xs);ymin,ymax=min(0,min(ys)),max(ys)*1.05
        if xmax<=xmin:xmax=xmin+1
        if ymax<=ymin:ymax=ymin+1
        px=lambda x:l+(x-xmin)/(xmax-xmin)*(r-l);py=lambda y:bt-(y-ymin)/(ymax-ymin)*(bt-t)
        for i in range(6):
            v=ymin+(ymax-ymin)*i/5;yy=py(v);c.create_line(l,yy,r,yy,fill="#e8edf3");c.create_text(l-7,yy,text=f"{v:,.0f}",anchor="e",fill="#5d6672",font=("맑은 고딕",8))
        c.create_line(l,t,l,bt,fill="#444");c.create_line(l,bt,r,bt,fill="#444")
        for x,y in self.train:c.create_oval(px(x)-2,py(y)-2,px(x)+2,py(y)+2,fill="#6ba0d5",outline="")
        c.create_line(px(xmin),py(self.b+self.a*xmin),px(xmax),py(self.b+self.a*xmax),fill="#f08035",width=3)
        if self.pred is not None:
            try:x=float(self.area.get().replace(",",""))
            except ValueError:x=xmin
            if xmin<=x<=xmax and ymin<=self.pred<=ymax:c.create_text(px(x),py(self.pred),text="★",fill="#e65b48",font=("맑은 고딕",15,"bold"))
        c.create_text((l+r)/2,h-12,text="전용면적 (m²)",fill="#333",font=("맑은 고딕",9));c.create_text(14,(t+bt)/2,text="매매가격",angle=90,fill="#333",font=("맑은 고딕",9))
if __name__=="__main__":
    try:App().mainloop()
    except Exception as e:
        root=tk.Tk();root.withdraw();messagebox.showerror("프로그램을 시작할 수 없습니다",str(e))

