export function angle(a,b,c){const u=[a[0]-b[0],a[1]-b[1]],v=[c[0]-b[0],c[1]-b[1]],d=Math.hypot(...u)*Math.hypot(...v);return d<1e-8?null:Math.acos(Math.max(-1,Math.min(1,(u[0]*v[0]+u[1]*v[1])/d)))*180/Math.PI;}
export function lean(a,b){return Math.hypot(a[0]-b[0],a[1]-b[1])<1e-8?null:Math.atan2(Math.abs(a[0]-b[0]),Math.abs(a[1]-b[1]))*180/Math.PI;}
export function offset(p,a,b){const x=b[0]-a[0],y=b[1]-a[1],d=x*x+y*y;return d<1e-8?null:Math.abs(x*(p[1]-a[1])-y*(p[0]-a[0]))/d;}
