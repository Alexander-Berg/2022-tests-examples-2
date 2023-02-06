from data.lib import Data


class Data1(Data):
    content = """
Interface               Admin Link Proto    Local                 Remote
et-0/0/0                up    up
et-0/0/0.0              up    up   aenet    --> ae1.0
gr-0/0/0                up    up
pfe-0/0/0               up    up
pfe-0/0/0.16383         up    up   inet   
                                   inet6  
pfh-0/0/0               up    up
pfh-0/0/0.16383         up    up   inet   
pfh-0/0/0.16384         up    up   inet   
sxe-0/0/0               up    up
et-0/0/1                up    up
et-0/0/1.0              up    up   aenet    --> ae1.0
sxe-0/0/1               up    up
et-0/0/2                up    up
et-0/0/2.0              up    up   aenet    --> ae1.0
sxe-0/0/2               up    up
et-0/0/3                up    up
et-0/0/3.0              up    up   aenet    --> ae1.0
sxe-0/0/3               up    up
et-0/0/4                up    up
et-0/0/4.0              up    up   aenet    --> ae1.0
sxe-0/0/4               up    up
et-0/0/5                up    up
et-0/0/5.0              up    up   aenet    --> ae1.0
sxe-0/0/5               up    up
et-0/0/6                up    up
et-0/0/6.0              up    up   aenet    --> ae1.0
et-0/0/7                up    up
et-0/0/7.0              up    up   aenet    --> ae1.0
et-0/0/8                up    up
et-0/0/8.0              up    up   aenet    --> ae1.0
et-0/0/9                up    up
et-0/0/9.0              up    up   aenet    --> ae1.0
et-0/0/10               up    up
et-0/0/10.0             up    up   aenet    --> ae1.0
et-0/0/11               up    up
et-0/0/11.0             up    up   aenet    --> ae1.0
et-0/0/12               up    up
et-0/0/12.3000          up    up   inet6    fe80::c1:d1/64 
et-0/0/12.32767         up    up 
et-0/0/13               up    down
et-0/0/13.0             up    down
et-0/0/14               up    up
et-0/0/14.3000          up    up   inet6    fe80::c1:d1/64 
et-0/0/14.32767         up    up 
et-0/0/15               up    up
et-0/0/15.3000          up    up   inet6    fe80::c1:d1/64 
et-0/0/15.32767         up    up 
et-0/0/16               up    up
et-0/0/16.3000          up    up   inet6    fe80::c1:d1/64 
et-0/0/16.32767         up    up 
et-0/0/17               up    down
et-0/0/17.0             up    down
et-0/0/18               up    up
et-0/0/18.0             up    up   aenet    --> ae5.0
et-0/0/19               up    up
et-0/0/19.0             up    up   aenet    --> ae5.0
et-0/0/20               up    up
et-0/0/20.0             up    up   aenet    --> ae5.0
et-0/0/21               up    up
et-0/0/21.0             up    up   aenet    --> ae5.0
et-0/0/22               up    up
et-0/0/22.0             up    up   aenet    --> ae5.0
et-0/0/23               up    up
et-0/0/23.0             up    up   aenet    --> ae5.0
et-0/0/24               up    up
et-0/0/24.0             up    up   aenet    --> ae5.0
et-0/0/25               up    up
et-0/0/25.0             up    up   aenet    --> ae5.0
et-0/0/26               up    up
et-0/0/26.0             up    up   aenet    --> ae5.0
et-0/0/27               up    up
et-0/0/27.0             up    up   aenet    --> ae5.0
et-0/0/28               up    up
et-0/0/28.0             up    up   aenet    --> ae5.0
et-0/0/29               up    up
et-0/0/29.0             up    up   aenet    --> ae5.0
et-1/0/0                up    up
et-1/0/0.0              up    up   aenet    --> ae1.0
pfe-1/0/0               up    up
pfe-1/0/0.16383         up    up   inet   
                                   inet6  
pfh-1/0/0               up    up
pfh-1/0/0.16383         up    up   inet   
pfh-1/0/0.16384         up    up   inet   
sxe-1/0/0               up    up
et-1/0/1                up    up
et-1/0/1.0              up    up   aenet    --> ae1.0
sxe-1/0/1               up    up
et-1/0/2                up    up
et-1/0/2.0              up    up   aenet    --> ae1.0
sxe-1/0/2               up    up
et-1/0/3                up    up
et-1/0/3.0              up    up   aenet    --> ae1.0
sxe-1/0/3               up    up
et-1/0/4                up    up
et-1/0/4.0              up    up   aenet    --> ae1.0
sxe-1/0/4               up    up
et-1/0/5                up    up
et-1/0/5.0              up    up   aenet    --> ae1.0
sxe-1/0/5               up    up
et-1/0/6                up    up
et-1/0/6.0              up    up   aenet    --> ae1.0
et-1/0/7                up    up
et-1/0/7.0              up    up   aenet    --> ae1.0
et-1/0/8                up    up
et-1/0/8.0              up    up   aenet    --> ae1.0
et-1/0/9                up    up
et-1/0/9.0              up    up   aenet    --> ae1.0
et-1/0/10               up    up
et-1/0/10.0             up    up   aenet    --> ae1.0
et-1/0/11               up    up
et-1/0/11.0             up    up   aenet    --> ae1.0
et-1/0/12               up    down
et-1/0/12.0             up    down
et-1/0/13               up    up
et-1/0/13.3000          up    up   inet6    fe80::c1:d1/64 
et-1/0/13.32767         up    up 
et-1/0/14               up    down
et-1/0/14.0             up    down
et-1/0/15               up    down
et-1/0/15.3000          up    down inet6    fe80::c1:d1/64 
et-1/0/15.32767         up    down
et-1/0/16               up    up
et-1/0/16.3000          up    up   inet6    fe80::c1:d1/64 
et-1/0/16.32767         up    up 
et-1/0/17               up    up
et-1/0/17.3000          up    up   inet6    fe80::c1:d1/64 
et-1/0/17.32767         up    up 
et-1/0/18               up    up
et-1/0/18.0             up    up   aenet    --> ae5.0
et-1/0/19               up    up
et-1/0/19.0             up    up   aenet    --> ae5.0
et-1/0/20               up    up
et-1/0/20.0             up    up   aenet    --> ae5.0
et-1/0/21               up    up
et-1/0/21.0             up    up   aenet    --> ae5.0
et-1/0/22               up    up
et-1/0/22.0             up    up   aenet    --> ae5.0
et-1/0/23               up    up
et-1/0/23.0             up    up   aenet    --> ae5.0
et-1/0/24               up    up
et-1/0/24.0             up    up   aenet    --> ae5.0
et-1/0/25               up    up
et-1/0/25.0             up    up   aenet    --> ae5.0
et-1/0/26               up    up
et-1/0/26.0             up    up   aenet    --> ae5.0
et-1/0/27               up    up
et-1/0/27.0             up    up   aenet    --> ae5.0
et-1/0/28               up    up
et-1/0/28.0             up    up   aenet    --> ae5.0
et-1/0/29               up    up
et-1/0/29.0             up    up   aenet    --> ae5.0
et-2/0/0                up    up
et-2/0/0.0              up    up   aenet    --> ae3.0
pfe-2/0/0               up    up
pfe-2/0/0.16383         up    up   inet   
                                   inet6  
pfh-2/0/0               up    up
pfh-2/0/0.16383         up    up   inet   
pfh-2/0/0.16384         up    up   inet   
sxe-2/0/0               up    up
et-2/0/1                up    up
et-2/0/1.0              up    up   aenet    --> ae3.0
sxe-2/0/1               up    up
et-2/0/2                up    up
et-2/0/2.0              up    up   aenet    --> ae3.0
sxe-2/0/2               up    up
et-2/0/3                up    up
et-2/0/3.0              up    up   aenet    --> ae3.0
sxe-2/0/3               up    up
et-2/0/4                up    up
et-2/0/4.0              up    up   aenet    --> ae3.0
sxe-2/0/4               up    up
et-2/0/5                up    up
et-2/0/5.0              up    up   aenet    --> ae3.0
sxe-2/0/5               up    up
et-2/0/6                up    up
et-2/0/6.0              up    up   aenet    --> ae1.0
et-2/0/7                up    up
et-2/0/7.0              up    up   aenet    --> ae1.0
et-2/0/8                up    up
et-2/0/8.0              up    up   aenet    --> ae1.0
et-2/0/9                up    up
et-2/0/9.0              up    up   aenet    --> ae1.0
et-2/0/10               up    up
et-2/0/10.0             up    up   aenet    --> ae1.0
et-2/0/11               up    up
et-2/0/11.0             up    up   aenet    --> ae1.0
et-2/0/12               up    up
et-2/0/12.3000          up    up   inet6    fe80::c1:d1/64 
et-2/0/12.32767         up    up 
et-2/0/13               up    up
et-2/0/13.3000          up    up   inet6    fe80::c1:d1/64 
et-2/0/13.32767         up    up 
et-2/0/14               up    up
et-2/0/14.3000          up    up   inet6    fe80::c1:d1/64 
et-2/0/14.32767         up    up 
et-2/0/15               up    up
et-2/0/15.3000          up    up   inet6    fe80::c1:d1/64 
et-2/0/15.32767         up    up 
et-2/0/16               up    up
et-2/0/16.3000          up    up   inet6    fe80::c1:d1/64 
et-2/0/16.32767         up    up 
et-2/0/17               up    up
et-2/0/17.3000          up    up   inet6    fe80::c1:d1/64 
et-2/0/17.32767         up    up 
et-2/0/18               up    up
et-2/0/18.0             up    up   aenet    --> ae7.0
et-2/0/19               up    up
et-2/0/19.0             up    up   aenet    --> ae7.0
et-2/0/20               up    up
et-2/0/20.0             up    up   aenet    --> ae7.0
et-2/0/21               up    up
et-2/0/21.0             up    up   aenet    --> ae7.0
et-2/0/22               up    up
et-2/0/22.0             up    up   aenet    --> ae7.0
et-2/0/23               up    up
et-2/0/23.0             up    up   aenet    --> ae7.0
et-2/0/24               up    up
et-2/0/24.0             up    up   aenet    --> ae5.0
et-2/0/25               up    up
et-2/0/25.0             up    up   aenet    --> ae5.0
et-2/0/26               up    up
et-2/0/26.0             up    up   aenet    --> ae5.0
et-2/0/27               up    up
et-2/0/27.0             up    up   aenet    --> ae5.0
et-2/0/28               up    up
et-2/0/28.0             up    up   aenet    --> ae5.0
et-2/0/29               up    up
et-2/0/29.0             up    up   aenet    --> ae5.0
et-3/0/0                up    up
et-3/0/0.0              up    up   aenet    --> ae3.0
pfe-3/0/0               up    up
pfe-3/0/0.16383         up    up   inet   
                                   inet6  
pfh-3/0/0               up    up
pfh-3/0/0.16383         up    up   inet   
pfh-3/0/0.16384         up    up   inet   
sxe-3/0/0               up    up
et-3/0/1                up    up
et-3/0/1.0              up    up   aenet    --> ae3.0
sxe-3/0/1               up    up
et-3/0/2                up    up
et-3/0/2.0              up    up   aenet    --> ae3.0
sxe-3/0/2               up    up
et-3/0/3                up    up
et-3/0/3.0              up    up   aenet    --> ae3.0
sxe-3/0/3               up    up
et-3/0/4                up    up
et-3/0/4.0              up    up   aenet    --> ae3.0
sxe-3/0/4               up    up
et-3/0/5                up    up
et-3/0/5.0              up    up   aenet    --> ae3.0
sxe-3/0/5               up    up
et-3/0/6                up    up
et-3/0/6.0              up    up   aenet    --> ae3.0
et-3/0/7                up    up
et-3/0/7.0              up    up   aenet    --> ae3.0
et-3/0/8                up    up
et-3/0/8.0              up    up   aenet    --> ae3.0
et-3/0/9                up    up
et-3/0/9.0              up    up   aenet    --> ae3.0
et-3/0/10               up    up
et-3/0/10.0             up    up   aenet    --> ae3.0
et-3/0/11               up    up
et-3/0/11.0             up    up   aenet    --> ae3.0
et-3/0/12               up    up
et-3/0/12.3000          up    up   inet6    fe80::c1:d1/64 
et-3/0/12.32767         up    up 
et-3/0/13               up    up
et-3/0/13.3000          up    up   inet6    fe80::c1:d1/64 
et-3/0/13.32767         up    up 
et-3/0/14               up    up
et-3/0/14.3000          up    up   inet6    fe80::c1:d1/64 
et-3/0/14.32767         up    up 
et-3/0/15               up    up
et-3/0/15.3000          up    up   inet6    fe80::c1:d1/64 
et-3/0/15.32767         up    up 
et-3/0/16               up    up
et-3/0/16.3000          up    up   inet6    fe80::c1:d1/64 
et-3/0/16.32767         up    up 
et-3/0/17               up    down
et-3/0/17.0             up    down
et-3/0/18               up    up
et-3/0/18.0             up    up   aenet    --> ae7.0
et-3/0/19               up    up
et-3/0/19.0             up    up   aenet    --> ae7.0
et-3/0/20               up    up
et-3/0/20.0             up    up   aenet    --> ae7.0
et-3/0/21               up    up
et-3/0/21.0             up    up   aenet    --> ae7.0
et-3/0/22               up    up
et-3/0/22.0             up    up   aenet    --> ae7.0
et-3/0/23               up    up
et-3/0/23.0             up    up   aenet    --> ae7.0
et-3/0/24               up    up
et-3/0/24.0             up    up   aenet    --> ae7.0
et-3/0/25               up    up
et-3/0/25.0             up    up   aenet    --> ae7.0
et-3/0/26               up    up
et-3/0/26.0             up    up   aenet    --> ae7.0
et-3/0/27               up    up
et-3/0/27.0             up    up   aenet    --> ae7.0
et-3/0/28               up    up
et-3/0/28.0             up    up   aenet    --> ae7.0
et-3/0/29               up    up
et-3/0/29.0             up    up   aenet    --> ae7.0
et-4/0/0                up    up
et-4/0/0.0              up    up   aenet    --> ae3.0
pfe-4/0/0               up    up
pfe-4/0/0.16383         up    up   inet   
                                   inet6  
pfh-4/0/0               up    up
pfh-4/0/0.16383         up    up   inet   
pfh-4/0/0.16384         up    up   inet   
sxe-4/0/0               up    up
et-4/0/1                up    up
et-4/0/1.0              up    up   aenet    --> ae3.0
sxe-4/0/1               up    up
et-4/0/2                up    up
et-4/0/2.0              up    up   aenet    --> ae3.0
sxe-4/0/2               up    up
et-4/0/3                up    up
et-4/0/3.0              up    up   aenet    --> ae3.0
sxe-4/0/3               up    up
et-4/0/4                up    up
et-4/0/4.0              up    up   aenet    --> ae3.0
sxe-4/0/4               up    up
et-4/0/5                up    up
et-4/0/5.0              up    up   aenet    --> ae3.0
sxe-4/0/5               up    up
et-4/0/6                up    up
et-4/0/6.0              up    up   aenet    --> ae3.0
et-4/0/7                up    up
et-4/0/7.0              up    up   aenet    --> ae3.0
et-4/0/8                up    up
et-4/0/8.0              up    up   aenet    --> ae3.0
et-4/0/9                up    up
et-4/0/9.0              up    up   aenet    --> ae3.0
et-4/0/10               up    up
et-4/0/10.0             up    up   aenet    --> ae3.0
et-4/0/11               up    up
et-4/0/11.0             up    up   aenet    --> ae3.0
et-4/0/12               up    up
et-4/0/12.3000          up    up   inet6    fe80::c1:d1/64 
et-4/0/12.32767         up    up 
et-4/0/13               up    up
et-4/0/13.3000          up    up   inet6    fe80::c1:d1/64 
et-4/0/13.32767         up    up 
et-4/0/14               up    up
et-4/0/14.3000          up    up   inet6    fe80::c1:d1/64 
et-4/0/14.32767         up    up 
et-4/0/15               up    up
et-4/0/15.3000          up    up   inet6    fe80::c1:d1/64 
et-4/0/15.32767         up    up 
et-4/0/16               up    up
et-4/0/16.3000          up    up   inet6    fe80::c1:d1/64 
et-4/0/16.32767         up    up 
et-4/0/17               up    up
et-4/0/17.3000          up    up   inet6    fe80::c1:d1/64 
et-4/0/17.32767         up    up 
et-4/0/18               up    up
et-4/0/18.0             up    up   aenet    --> ae7.0
et-4/0/19               up    up
et-4/0/19.0             up    up   aenet    --> ae7.0
et-4/0/20               up    up
et-4/0/20.0             up    up   aenet    --> ae7.0
et-4/0/21               up    up
et-4/0/21.0             up    up   aenet    --> ae7.0
et-4/0/22               up    up
et-4/0/22.0             up    up   aenet    --> ae7.0
et-4/0/23               up    up
et-4/0/23.0             up    up   aenet    --> ae7.0
et-4/0/24               up    up
et-4/0/24.0             up    up   aenet    --> ae7.0
et-4/0/25               up    up
et-4/0/25.0             up    up   aenet    --> ae7.0
et-4/0/26               up    up
et-4/0/26.0             up    up   aenet    --> ae7.0
et-4/0/27               up    up
et-4/0/27.0             up    up   aenet    --> ae7.0
et-4/0/28               up    up
et-4/0/28.0             up    up   aenet    --> ae7.0
et-4/0/29               up    up
et-4/0/29.0             up    up   aenet    --> ae7.0
et-5/0/0                up    up
et-5/0/0.0              up    up   aenet    --> ae1.0
pfe-5/0/0               up    up
pfe-5/0/0.16383         up    up   inet   
                                   inet6  
pfh-5/0/0               up    up
pfh-5/0/0.16383         up    up   inet   
pfh-5/0/0.16384         up    up   inet   
sxe-5/0/0               up    up
et-5/0/1                up    up
et-5/0/1.0              up    up   aenet    --> ae1.0
sxe-5/0/1               up    up
et-5/0/2                up    up
et-5/0/2.0              up    up   aenet    --> ae1.0
sxe-5/0/2               up    up
et-5/0/3                up    up
et-5/0/3.0              up    up   aenet    --> ae1.0
sxe-5/0/3               up    up
et-5/0/4                up    up
et-5/0/4.0              up    up   aenet    --> ae1.0
sxe-5/0/4               up    up
et-5/0/5                up    up
et-5/0/5.0              up    up   aenet    --> ae1.0
sxe-5/0/5               up    up
et-5/0/6                up    up
et-5/0/6.0              up    up   aenet    --> ae1.0
et-5/0/7                up    up
et-5/0/7.0              up    up   aenet    --> ae1.0
et-5/0/8                up    up
et-5/0/8.0              up    up   aenet    --> ae1.0
et-5/0/9                up    up
et-5/0/9.0              up    up   aenet    --> ae1.0
et-5/0/10               up    up
et-5/0/10.0             up    up   aenet    --> ae1.0
et-5/0/11               up    up
et-5/0/11.0             up    up   aenet    --> ae1.0
et-5/0/12               up    down
et-5/0/12.0             up    down
et-5/0/13               up    up
et-5/0/13.3000          up    up   inet6    fe80::c1:d1/64 
et-5/0/13.32767         up    up 
et-5/0/14               up    up
et-5/0/14.3000          up    up   inet6    fe80::c1:d1/64 
et-5/0/14.32767         up    up 
et-5/0/15               up    up
et-5/0/15.3000          up    up   inet6    fe80::c1:d1/64 
et-5/0/15.32767         up    up 
et-5/0/16               up    down
et-5/0/16.0             up    down
et-5/0/17               up    down
et-5/0/17.0             up    down
et-5/0/18               up    up
et-5/0/18.0             up    up   aenet    --> ae5.0
et-5/0/19               up    up
et-5/0/19.0             up    up   aenet    --> ae5.0
et-5/0/20               up    up
et-5/0/20.0             up    up   aenet    --> ae5.0
et-5/0/21               up    up
et-5/0/21.0             up    up   aenet    --> ae5.0
et-5/0/22               up    up
et-5/0/22.0             up    up   aenet    --> ae5.0
et-5/0/23               up    up
et-5/0/23.0             up    up   aenet    --> ae5.0
et-5/0/24               up    up
et-5/0/24.0             up    up   aenet    --> ae5.0
et-5/0/25               up    up
et-5/0/25.0             up    up   aenet    --> ae5.0
et-5/0/26               up    up
et-5/0/26.0             up    up   aenet    --> ae5.0
et-5/0/27               up    up
et-5/0/27.0             up    up   aenet    --> ae5.0
et-5/0/28               up    up
et-5/0/28.0             up    up   aenet    --> ae5.0
et-5/0/29               up    up
et-5/0/29.0             up    up   aenet    --> ae5.0
et-6/0/0                up    up
et-6/0/0.0              up    up   aenet    --> ae3.0
pfe-6/0/0               up    up
pfe-6/0/0.16383         up    up   inet   
                                   inet6  
pfh-6/0/0               up    up
pfh-6/0/0.16383         up    up   inet   
pfh-6/0/0.16384         up    up   inet   
sxe-6/0/0               up    up
et-6/0/1                up    up
et-6/0/1.0              up    up   aenet    --> ae3.0
sxe-6/0/1               up    up
et-6/0/2                up    up
et-6/0/2.0              up    up   aenet    --> ae3.0
sxe-6/0/2               up    up
et-6/0/3                up    up
et-6/0/3.0              up    up   aenet    --> ae3.0
sxe-6/0/3               up    up
et-6/0/4                up    up
et-6/0/4.0              up    up   aenet    --> ae3.0
sxe-6/0/4               up    up
et-6/0/5                up    up
et-6/0/5.0              up    up   aenet    --> ae3.0
sxe-6/0/5               up    up
et-6/0/6                up    up
et-6/0/6.0              up    up   aenet    --> ae3.0
et-6/0/7                up    up
et-6/0/7.0              up    up   aenet    --> ae3.0
et-6/0/8                up    up
et-6/0/8.0              up    up   aenet    --> ae3.0
et-6/0/9                up    up
et-6/0/9.0              up    up   aenet    --> ae3.0
et-6/0/10               up    up
et-6/0/10.0             up    up   aenet    --> ae3.0
et-6/0/11               up    up
et-6/0/11.0             up    up   aenet    --> ae3.0
et-6/0/12               up    up
et-6/0/12.3000          up    up   inet6    fe80::c1:d1/64 
et-6/0/12.32767         up    up 
et-6/0/13               up    up
et-6/0/13.3000          up    up   inet6    fe80::c1:d1/64 
et-6/0/13.32767         up    up 
et-6/0/14               up    up
et-6/0/14.3000          up    up   inet6    fe80::c1:d1/64 
et-6/0/14.32767         up    up 
et-6/0/15               up    down
et-6/0/15.0             up    down
et-6/0/16               up    up
et-6/0/16.3000          up    up   inet6    fe80::c1:d1/64 
et-6/0/16.32767         up    up 
et-6/0/17               up    up
et-6/0/17.3000          up    up   inet6    fe80::c1:d1/64 
et-6/0/17.32767         up    up 
et-6/0/18               up    up
et-6/0/18.0             up    up   aenet    --> ae7.0
et-6/0/19               up    down
et-6/0/19.0             up    down
et-6/0/20               up    up
et-6/0/20.0             up    up   aenet    --> ae7.0
et-6/0/21               up    up
et-6/0/21.0             up    up   aenet    --> ae7.0
et-6/0/22               up    up
et-6/0/22.0             up    up   aenet    --> ae7.0
et-6/0/23               up    up
et-6/0/23.0             up    up   aenet    --> ae7.0
et-6/0/24               up    up
et-6/0/24.0             up    up   aenet    --> ae7.0
et-6/0/25               up    up
et-6/0/25.0             up    up   aenet    --> ae7.0
et-6/0/26               up    up
et-6/0/26.0             up    up   aenet    --> ae7.0
et-6/0/27               up    up
et-6/0/27.0             up    up   aenet    --> ae7.0
et-6/0/28               up    up
et-6/0/28.0             up    up   aenet    --> ae7.0
et-6/0/29               up    up
et-6/0/29.0             up    up   aenet    --> ae7.0
et-7/0/0                up    up
et-7/0/0.0              up    up   aenet    --> ae7.0
pfe-7/0/0               up    up
pfe-7/0/0.16383         up    up   inet   
                                   inet6  
pfh-7/0/0               up    up
pfh-7/0/0.16383         up    up   inet   
pfh-7/0/0.16384         up    up   inet   
sxe-7/0/0               up    up
et-7/0/1                up    up
et-7/0/1.0              up    up   aenet    --> ae7.0
sxe-7/0/1               up    up
et-7/0/2                up    up
et-7/0/2.0              up    up   aenet    --> ae7.0
sxe-7/0/2               up    up
et-7/0/3                up    up
et-7/0/3.0              up    up   aenet    --> ae5.0
sxe-7/0/3               up    up
et-7/0/4                up    up
et-7/0/4.0              up    up   aenet    --> ae5.0
sxe-7/0/4               up    up
et-7/0/5                up    up
et-7/0/5.0              up    up   aenet    --> ae5.0
sxe-7/0/5               up    up
et-7/0/6                up    up
et-7/0/6.0              up    up   aenet    --> ae3.0
et-7/0/7                up    up
et-7/0/7.0              up    up   aenet    --> ae3.0
et-7/0/8                up    up
et-7/0/8.0              up    up   aenet    --> ae3.0
et-7/0/9                up    up
et-7/0/9.0              up    up   aenet    --> ae1.0
et-7/0/10               up    up
et-7/0/10.0             up    up   aenet    --> ae1.0
et-7/0/11               up    up
et-7/0/11.0             up    up   aenet    --> ae1.0
et-7/0/12               up    up
et-7/0/12.3000          up    up   inet6    fe80::c1:d1/64 
et-7/0/12.32767         up    up 
et-7/0/13               up    up
et-7/0/13.3000          up    up   inet6    fe80::c1:d1/64 
et-7/0/13.32767         up    up 
et-7/0/14               up    up
et-7/0/14.3000          up    up   inet6    fe80::c1:d1/64 
et-7/0/14.32767         up    up 
et-7/0/15               up    up
et-7/0/15.3000          up    up   inet6    fe80::c1:d1/64 
et-7/0/15.32767         up    up 
et-7/0/16               up    up
et-7/0/16.3000          up    up   inet6    fe80::c1:d1/64 
et-7/0/16.32767         up    up 
et-7/0/17               up    up
et-7/0/17.3000          up    up   inet6    fe80::c1:d1/64 
et-7/0/17.32767         up    up 
et-7/0/19               up    up
et-7/0/19.3000          up    up   aenet    --> ae102.3000
et-7/0/19.3666          up    up   aenet    --> ae102.3666
et-7/0/19.32767         up    up   aenet    --> ae102.32767
et-7/0/20               up    down
et-7/0/21               up    up
et-7/0/22               up    up
et-7/0/22.3000          up    up   aenet    --> ae101.3000
et-7/0/22.3666          up    up   aenet    --> ae101.3666
et-7/0/22.32767         up    up   aenet    --> ae101.32767
et-8/0/0                up    up
et-8/0/0.3000           up    up   inet6    fe80::c1:d1/64 
et-8/0/0.32767          up    up 
pfe-8/0/0               up    up
pfe-8/0/0.16383         up    up   inet   
                                   inet6  
pfh-8/0/0               up    up
pfh-8/0/0.16383         up    up   inet   
pfh-8/0/0.16384         up    up   inet   
sxe-8/0/0               up    up
et-8/0/1                up    up
et-8/0/1.3000           up    up   inet6    fe80::c1:d1/64 
et-8/0/1.32767          up    up 
sxe-8/0/1               up    up
et-8/0/2                up    up
et-8/0/2.3000           up    up   inet6    fe80::c1:d1/64 
et-8/0/2.32767          up    up 
sxe-8/0/2               up    up
et-8/0/3                up    up
et-8/0/3.3000           up    up   inet6    fe80::c1:d1/64 
et-8/0/3.32767          up    up 
sxe-8/0/3               up    up
et-8/0/4                up    up
et-8/0/4.3000           up    up   inet6    fe80::c1:d1/64 
et-8/0/4.32767          up    up 
sxe-8/0/4               up    up
et-8/0/5                up    up
et-8/0/5.3000           up    up   inet6    fe80::c1:d1/64 
et-8/0/5.32767          up    up 
sxe-8/0/5               up    up
et-8/0/6                up    up
et-8/0/6.3000           up    up   inet6    fe80::c1:d1/64 
et-8/0/6.32767          up    up 
et-8/0/7                up    up
et-8/0/7.3000           up    up   inet6    fe80::c1:d1/64 
et-8/0/7.32767          up    up 
et-8/0/8                up    up
et-8/0/8.3000           up    up   inet6    fe80::c1:d1/64 
et-8/0/8.32767          up    up 
et-8/0/9                up    up
et-8/0/9.3000           up    up   inet6    fe80::c1:d1/64 
et-8/0/9.32767          up    up 
et-8/0/10               up    up
et-8/0/10.3000          up    up   inet6    fe80::c1:d1/64 
et-8/0/10.32767         up    up 
et-8/0/11               up    up
et-8/0/11.3000          up    up   inet6    fe80::c1:d1/64 
et-8/0/11.32767         up    up 
et-8/0/12               up    up
et-8/0/12.3000          up    up   inet6    fe80::c1:d1/64 
et-8/0/12.32767         up    up 
et-8/0/13               up    down
et-8/0/13.0             up    down
et-8/0/14               up    up
et-8/0/14.3000          up    up   inet6    fe80::c1:d1/64 
et-8/0/14.32767         up    up 
et-8/0/15               up    down
et-8/0/15.0             up    down
et-8/0/16               up    up
et-8/0/16.3000          up    up   inet6    fe80::c1:d1/64 
et-8/0/16.32767         up    up 
et-8/0/17               up    down
et-8/0/17.0             up    down
et-8/0/18               up    down
et-8/0/18.0             up    down
et-8/0/19               up    up
et-8/0/19.3000          up    up   inet6    fe80::c1:d1/64 
et-8/0/19.32767         up    up 
et-8/0/20               up    up
et-8/0/20.3000          up    up   inet6    fe80::c1:d1/64 
et-8/0/20.32767         up    up 
et-8/0/21               up    up
et-8/0/21.3000          up    up   inet6    fe80::c1:d1/64 
et-8/0/21.32767         up    up 
et-8/0/22               up    down
et-8/0/22.0             up    down
et-8/0/23               up    up
et-8/0/23.3000          up    up   inet6    fe80::c1:d1/64 
et-8/0/23.32767         up    up 
et-8/0/24               up    down
et-8/0/24.0             up    down
et-8/0/25               up    down
et-8/0/25.0             up    down
et-8/0/26               up    down
et-8/0/26.0             up    down
et-8/0/27               up    up
et-8/0/27.3000          up    up   inet6    fe80::c1:d1/64 
et-8/0/27.32767         up    up 
et-8/0/28               up    up
et-8/0/28.3000          up    up   inet6    fe80::c1:d1/64 
et-8/0/28.32767         up    up 
et-8/0/29               up    up
et-8/0/29.3000          up    up   inet6    fe80::c1:d1/64 
et-8/0/29.32767         up    up 
et-9/0/0                up    up
et-9/0/0.3000           up    up   inet6    fe80::c1:d1/64 
et-9/0/0.32767          up    up 
pfe-9/0/0               up    up
pfe-9/0/0.16383         up    up   inet   
                                   inet6  
pfh-9/0/0               up    up
pfh-9/0/0.16383         up    up   inet   
pfh-9/0/0.16384         up    up   inet   
sxe-9/0/0               up    up
et-9/0/1                up    up
et-9/0/1.3000           up    up   inet6    fe80::c1:d1/64 
et-9/0/1.32767          up    up 
sxe-9/0/1               up    up
et-9/0/2                up    up
et-9/0/2.3000           up    up   inet6    fe80::c1:d1/64 
et-9/0/2.32767          up    up 
sxe-9/0/2               up    up
et-9/0/3                up    down
et-9/0/3.0              up    down
sxe-9/0/3               up    up
et-9/0/4                up    up
et-9/0/4.3000           up    up   inet6    fe80::c1:d1/64 
et-9/0/4.32767          up    up 
sxe-9/0/4               up    up
et-9/0/5                up    up
et-9/0/5.3000           up    up   inet6    fe80::c1:d1/64 
et-9/0/5.32767          up    up 
sxe-9/0/5               up    up
et-9/0/6                up    up
et-9/0/6.3000           up    up   inet6    fe80::c1:d1/64 
et-9/0/6.32767          up    up 
et-9/0/7                up    down
et-9/0/7.0              up    down
et-9/0/8                up    up
et-9/0/8.3000           up    up   inet6    fe80::c1:d1/64 
et-9/0/8.32767          up    up 
et-9/0/9                up    up
et-9/0/9.3000           up    up   inet6    fe80::c1:d1/64 
et-9/0/9.32767          up    up 
et-9/0/10               up    up
et-9/0/10.3000          up    up   inet6    fe80::c1:d1/64 
et-9/0/10.32767         up    up 
et-9/0/11               up    up
et-9/0/11.3000          up    up   inet6    fe80::c1:d1/64 
et-9/0/11.32767         up    up 
et-9/0/12               up    up
et-9/0/12.3000          up    up   inet6    fe80::c1:d1/64 
et-9/0/12.32767         up    up 
et-9/0/13               up    up
et-9/0/13.3000          up    up   inet6    fe80::c1:d1/64 
et-9/0/13.32767         up    up 
et-9/0/14               up    down
et-9/0/14.0             up    down
et-9/0/15               up    down
et-9/0/15.0             up    down
et-9/0/16               up    up
et-9/0/16.3000          up    up   inet6    fe80::c1:d1/64 
et-9/0/16.32767         up    up 
et-9/0/17               up    up
et-9/0/17.3000          up    up   inet6    fe80::c1:d1/64 
et-9/0/17.32767         up    up 
et-9/0/18               up    up
et-9/0/18.3000          up    up   inet6    fe80::c1:d1/64 
et-9/0/18.32767         up    up 
et-9/0/19               up    up
et-9/0/19.3000          up    up   inet6    fe80::c1:d1/64 
et-9/0/19.32767         up    up 
et-9/0/20               up    up
et-9/0/20.3000          up    up   inet6    fe80::c1:d1/64 
et-9/0/20.32767         up    up 
et-9/0/21               up    down
et-9/0/21.0             up    down
et-9/0/22               up    up
et-9/0/22.3000          up    up   inet6    fe80::c1:d1/64 
et-9/0/22.32767         up    up 
et-9/0/23               up    up
et-9/0/23.3000          up    up   inet6    fe80::c1:d1/64 
et-9/0/23.32767         up    up 
et-9/0/24               up    up
et-9/0/24.3000          up    up   inet6    fe80::c1:d1/64 
et-9/0/24.32767         up    up 
et-9/0/25               up    down
et-9/0/25.0             up    down
et-9/0/26               up    up
et-9/0/26.3000          up    up   inet6    fe80::c1:d1/64 
et-9/0/26.32767         up    up 
et-9/0/27               up    up
et-9/0/27.3000          up    up   inet6    fe80::c1:d1/64 
et-9/0/27.32767         up    up 
et-9/0/28               up    up
et-9/0/28.3000          up    up   inet6    fe80::c1:d1/64 
et-9/0/28.32767         up    up 
et-9/0/29               up    down
et-9/0/29.0             up    down
et-10/0/0               up    up
et-10/0/0.3000          up    up   inet6    fe80::c1:d1/64 
et-10/0/0.32767         up    up 
pfe-10/0/0              up    up
pfe-10/0/0.16383        up    up   inet   
                                   inet6  
pfh-10/0/0              up    up
pfh-10/0/0.16383        up    up   inet   
pfh-10/0/0.16384        up    up   inet   
sxe-10/0/0              up    up
et-10/0/1               up    up
et-10/0/1.3000          up    up   inet6    fe80::c1:d1/64 
et-10/0/1.32767         up    up 
sxe-10/0/1              up    up
et-10/0/2               up    up
et-10/0/2.3000          up    up   inet6    fe80::c1:d1/64 
et-10/0/2.32767         up    up 
sxe-10/0/2              up    up
et-10/0/3               up    up
et-10/0/3.3000          up    up   inet6    fe80::c1:d1/64 
et-10/0/3.32767         up    up 
sxe-10/0/3              up    up
et-10/0/4               up    up
et-10/0/4.3000          up    up   inet6    fe80::c1:d1/64 
et-10/0/4.32767         up    up 
sxe-10/0/4              up    up
et-10/0/5               up    up
et-10/0/5.3000          up    up   inet6    fe80::c1:d1/64 
et-10/0/5.32767         up    up 
sxe-10/0/5              up    up
et-10/0/6               up    up
et-10/0/6.3000          up    up   inet6    fe80::c1:d1/64 
et-10/0/6.32767         up    up 
et-10/0/7               up    up
et-10/0/7.3000          up    up   inet6    fe80::c1:d1/64 
et-10/0/7.32767         up    up 
et-10/0/8               up    up
et-10/0/8.3000          up    up   inet6    fe80::c1:d1/64 
et-10/0/8.32767         up    up 
et-10/0/9               up    up
et-10/0/9.3000          up    up   inet6    fe80::c1:d1/64 
et-10/0/9.32767         up    up 
et-10/0/10              up    up
et-10/0/10.3000         up    up   inet6    fe80::c1:d1/64 
et-10/0/10.32767        up    up 
et-10/0/11              up    up
et-10/0/11.3000         up    up   inet6    fe80::c1:d1/64 
et-10/0/11.32767        up    up 
et-10/0/12              up    down
et-10/0/12.0            up    down
et-10/0/13              up    down
et-10/0/13.0            up    down
et-10/0/18              up    up
et-10/0/18.3000         up    up   inet6    fe80::c1:d1/64 
et-10/0/18.32767        up    up 
et-10/0/19              up    down
et-10/0/19.0            up    down
et-10/0/20              up    up
et-10/0/20.3000         up    up   inet6    fe80::c1:d1/64 
et-10/0/20.32767        up    up 
et-10/0/21              up    up
et-10/0/21.3000         up    up   inet6    fe80::c1:d1/64 
et-10/0/21.32767        up    up 
et-10/0/22              up    up
et-10/0/22.3000         up    up   inet6    fe80::c1:d1/64 
et-10/0/22.32767        up    up 
et-10/0/23              up    down
et-10/0/23.0            up    down
et-10/0/24              up    down
et-10/0/24.0            up    down
et-10/0/25              up    up
et-10/0/25.3000         up    up   inet6    fe80::c1:d1/64 
et-10/0/25.32767        up    up 
et-10/0/26              up    up
et-10/0/26.3000         up    up   inet6    fe80::c1:d1/64 
et-10/0/26.32767        up    up 
et-10/0/27              up    up
et-10/0/27.3000         up    up   inet6    fe80::c1:d1/64 
et-10/0/27.32767        up    up 
et-10/0/28              up    up
et-10/0/28.3000         up    up   inet6    fe80::c1:d1/64 
et-10/0/28.32767        up    up 
et-10/0/29              up    up
et-10/0/29.3000         up    up   inet6    fe80::c1:d1/64 
et-10/0/29.32767        up    up 
et-11/0/0               up    up
et-11/0/0.3000          up    up   inet6    fe80::c1:d1/64 
et-11/0/0.32767         up    up 
pfe-11/0/0              up    up
pfe-11/0/0.16383        up    up   inet   
                                   inet6  
pfh-11/0/0              up    up
pfh-11/0/0.16383        up    up   inet   
pfh-11/0/0.16384        up    up   inet   
sxe-11/0/0              up    up
et-11/0/1               up    down
et-11/0/1.0             up    down
sxe-11/0/1              up    up
et-11/0/2               up    up
et-11/0/2.3000          up    up   inet6    fe80::c1:d1/64 
et-11/0/2.32767         up    up 
sxe-11/0/2              up    up
et-11/0/3               up    down
et-11/0/3.0             up    down
sxe-11/0/3              up    up
et-11/0/4               up    up
et-11/0/4.3000          up    up   inet6    fe80::c1:d1/64 
et-11/0/4.32767         up    up 
sxe-11/0/4              up    up
et-11/0/5               up    up
et-11/0/5.3000          up    up   inet6    fe80::c1:d1/64 
et-11/0/5.32767         up    up 
sxe-11/0/5              up    up
et-11/0/6               up    up
et-11/0/6.3000          up    up   inet6    fe80::c1:d1/64 
et-11/0/6.32767         up    up 
et-11/0/7               up    up
et-11/0/7.3000          up    up   inet6    fe80::c1:d1/64 
et-11/0/7.32767         up    up 
et-11/0/8               up    up
et-11/0/8.3000          up    up   inet6    fe80::c1:d1/64 
et-11/0/8.32767         up    up 
et-11/0/9               up    up
et-11/0/9.3000          up    up   inet6    fe80::c1:d1/64 
et-11/0/9.32767         up    up 
et-11/0/10              up    up
et-11/0/10.3000         up    up   inet6    fe80::c1:d1/64 
et-11/0/10.32767        up    up 
et-11/0/11              up    up
et-11/0/11.3000         up    up   inet6    fe80::c1:d1/64 
et-11/0/11.32767        up    up 
et-11/0/12              up    down
et-11/0/12.0            up    down
et-11/0/13              up    down
et-11/0/13.0            up    down
et-11/0/14              up    up
et-11/0/14.3000         up    up   inet6    fe80::c1:d1/64 
et-11/0/14.32767        up    up 
et-11/0/15              up    up
et-11/0/15.3000         up    up   inet6    fe80::c1:d1/64 
et-11/0/15.32767        up    up 
et-11/0/16              up    up
et-11/0/16.3000         up    up   inet6    fe80::c1:d1/64 
et-11/0/16.32767        up    up 
et-11/0/17              up    down
et-11/0/17.0            up    down
et-11/0/18              up    up
et-11/0/18.3000         up    up   inet6    fe80::c1:d1/64 
et-11/0/18.32767        up    up 
et-11/0/19              up    up
et-11/0/19.3000         up    up   inet6    fe80::c1:d1/64 
et-11/0/19.32767        up    up 
et-11/0/20              up    up
et-11/0/20.3000         up    up   inet6    fe80::c1:d1/64 
et-11/0/20.32767        up    up 
et-11/0/21              up    up
et-11/0/21.3000         up    up   inet6    fe80::c1:d1/64 
et-11/0/21.32767        up    up 
et-11/0/22              up    up
et-11/0/22.3000         up    up   inet6    fe80::c1:d1/64 
et-11/0/22.32767        up    up 
et-11/0/23              up    up
et-11/0/23.3000         up    up   inet6    fe80::c1:d1/64 
et-11/0/23.32767        up    up 
et-11/0/24              up    up
et-11/0/24.3000         up    up   inet6    fe80::c1:d1/64 
et-11/0/24.32767        up    up 
et-11/0/25              up    down
et-11/0/25.0            up    down
et-11/0/26              up    up
et-11/0/26.3000         up    up   inet6    fe80::c1:d1/64 
et-11/0/26.32767        up    up 
et-11/0/27              up    up
et-11/0/27.3000         up    up   inet6    fe80::c1:d1/64 
et-11/0/27.32767        up    up 
et-11/0/28              up    up
et-11/0/28.3000         up    up   inet6    fe80::c1:d1/64 
et-11/0/28.32767        up    up 
et-11/0/29              up    down
et-11/0/29.3000         up    down inet6    fe80::c1:d1/64 
et-11/0/29.32767        up    down
et-12/0/0               up    up
et-12/0/0.3000          up    up   inet6    fe80::c1:d1/64 
et-12/0/0.32767         up    up 
pfe-12/0/0              up    up
pfe-12/0/0.16383        up    up   inet   
                                   inet6  
pfh-12/0/0              up    up
pfh-12/0/0.16383        up    up   inet   
pfh-12/0/0.16384        up    up   inet   
sxe-12/0/0              up    up
et-12/0/1               up    up
et-12/0/1.3000          up    up   inet6    fe80::c1:d1/64 
et-12/0/1.32767         up    up 
sxe-12/0/1              up    up
et-12/0/2               up    up
et-12/0/2.3000          up    up   inet6    fe80::c1:d1/64 
et-12/0/2.32767         up    up 
sxe-12/0/2              up    up
et-12/0/3               up    down
et-12/0/3.0             up    down
sxe-12/0/3              up    up
et-12/0/4               up    down
et-12/0/4.0             up    down
sxe-12/0/4              up    up
et-12/0/5               up    up
et-12/0/5.3000          up    up   inet6    fe80::c1:d1/64 
et-12/0/5.32767         up    up 
sxe-12/0/5              up    up
et-12/0/6               up    down
et-12/0/6.0             up    down
et-12/0/7               up    down
et-12/0/7.0             up    down
et-12/0/8               up    up
et-12/0/8.3000          up    up   inet6    fe80::c1:d1/64 
et-12/0/8.32767         up    up 
et-12/0/9               up    up
et-12/0/9.3000          up    up   inet6    fe80::c1:d1/64 
et-12/0/9.32767         up    up 
et-12/0/10              up    up
et-12/0/10.3000         up    up   inet6    fe80::c1:d1/64 
et-12/0/10.32767        up    up 
et-12/0/11              up    up
et-12/0/11.3000         up    up   inet6    fe80::c1:d1/64 
et-12/0/11.32767        up    up 
et-12/0/13              up    up
et-12/0/13.3000         up    up   aenet    --> ae102.3000
et-12/0/13.3666         up    up   aenet    --> ae102.3666
et-12/0/13.32767        up    up   aenet    --> ae102.32767
et-12/0/15              up    up
et-12/0/15.3000         up    up   aenet    --> ae101.3000
et-12/0/15.3666         up    up   aenet    --> ae101.3666
et-12/0/15.32767        up    up   aenet    --> ae101.32767
et-12/0/18              up    up
et-12/0/18.3000         up    up   inet6    fe80::c1:d1/64 
et-12/0/18.32767        up    up 
et-12/0/19              up    up
et-12/0/19.3000         up    up   inet6    fe80::c1:d1/64 
et-12/0/19.32767        up    up 
et-12/0/20              up    up
et-12/0/20.3000         up    up   inet6    fe80::c1:d1/64 
et-12/0/20.32767        up    up 
et-12/0/21              up    up
et-12/0/21.3000         up    up   inet6    fe80::c1:d1/64 
et-12/0/21.32767        up    up 
et-12/0/22              up    up
et-12/0/22.3000         up    up   inet6    fe80::c1:d1/64 
et-12/0/22.32767        up    up 
et-12/0/23              up    up
et-12/0/23.3000         up    up   inet6    fe80::c1:d1/64 
et-12/0/23.32767        up    up 
et-12/0/24              up    up
et-12/0/24.3000         up    up   inet6    fe80::c1:d1/64 
et-12/0/24.32767        up    up 
et-12/0/25              up    up
et-12/0/25.3000         up    up   inet6    fe80::c1:d1/64 
et-12/0/25.32767        up    up 
et-12/0/26              up    up
et-12/0/26.3000         up    up   inet6    fe80::c1:d1/64 
et-12/0/26.32767        up    up 
et-12/0/27              up    up
et-12/0/27.3000         up    up   inet6    fe80::c1:d1/64 
et-12/0/27.32767        up    up 
et-12/0/28              up    up
et-12/0/28.3000         up    up   inet6    fe80::c1:d1/64 
et-12/0/28.32767        up    up 
et-12/0/29              up    up
et-12/0/29.3000         up    up   inet6    fe80::c1:d1/64 
et-12/0/29.32767        up    up 
ae1                     up    up
ae1.0                   up    up   inet     87.250.239.154/31
                                   inet6    fe80::2e21:31ff:fe65:f68f/64
                                   mpls   
ae3                     up    up
ae3.0                   up    up   inet     87.250.239.180/31
                                   inet6    fe80::2e21:31ff:fe65:f690/64
                                   mpls   
ae5                     up    up
ae5.0                   up    up   inet     87.250.239.182/31
                                   inet6    fe80::2e21:31ff:fe65:f691/64
                                   mpls   
ae7                     up    up
ae7.0                   up    up   inet     87.250.239.80/31
                                   inet6    fe80::2e21:31ff:fe65:f692/64
                                   mpls   
ae101                   up    up
ae101.3000              up    up   inet6    fe80::c1:d1/64 
ae101.3666              up    up   inet     10.1.1.254/24  
                                   inet6    fe80::c1:d1/64 
ae101.32767             up    up 
ae102                   up    up
ae102.3000              up    up   inet6    fe80::c1:d1/64 
ae102.3666              up    up   inet     10.2.1.254/24  
                                   inet6    fe80::c1:d1/64 
ae102.32767             up    up 
bme0                    up    up
bme0.0                  up    up   inet     128.0.0.1/2    
                                            128.0.0.4/2    
                                            128.0.0.63/2   
bme1                    up    up
bme1.0                  up    up   inet     128.0.0.1/2    
                                            128.0.0.4/2    
bme2                    up    up
bme2.0                  up    up   inet     128.0.0.1/2    
                                            128.0.0.4/2    
cbp0                    up    up
dsc                     up    up
em0                     up    up
em0.0                   up    up   inet     93.158.171.209      --> 0/0
em1                     up    down
em2                     up    up
em2.32768               up    up   inet     192.168.1.2/24 
esi                     up    up
gre                     up    up
ipip                    up    up
irb                     up    up
jsrv                    up    up
jsrv.1                  up    up   inet     128.0.0.127/2  
lo0                     up    up
lo0.0                   up    up   inet     95.108.237.168      --> 0/0
                                            127.0.0.1           --> 0/0
                                   inet6    fe80::2e21:310f:fcbb:754a
lo0.16385               up    up   inet   
lsi                     up    up
lsi.0                   up    up   inet   
                                   iso    
                                   inet6  
mtun                    up    up
pimd                    up    up
pime                    up    up
pip0                    up    up
tap                     up    up
vtep                    up    up

{master}
    """
    cmd = "show interfaces terse"
    host = "vla1-1d1"
    version = """
Hostname: vla1-1d1
Model: qfx10016
Junos: 18.2R2.6
JUNOS OS Kernel 64-bit  [20181108.217da31_builder_stable_11]
JUNOS OS libs [20181108.217da31_builder_stable_11]
JUNOS OS runtime [20181108.217da31_builder_stable_11]
JUNOS OS time zone information [20181108.217da31_builder_stable_11]
JUNOS OS libs compat32 [20181108.217da31_builder_stable_11]
JUNOS OS 32-bit compatibility [20181108.217da31_builder_stable_11]
JUNOS py extensions [20181207.090423_builder_junos_182_r2]
JUNOS py base [20181207.090423_builder_junos_182_r2]
JUNOS OS vmguest [20181108.217da31_builder_stable_11]
JUNOS OS crypto [20181108.217da31_builder_stable_11]
JUNOS network stack and utilities [20181207.090423_builder_junos_182_r2]
JUNOS libs [20181207.090423_builder_junos_182_r2]
JUNOS libs compat32 [20181207.090423_builder_junos_182_r2]
JUNOS runtime [20181207.090423_builder_junos_182_r2]
JUNOS Web Management Platform Package [20181207.090423_builder_junos_182_r2]
JUNOS qfx runtime [20181207.090423_builder_junos_182_r2]
JUNOS common platform support [20181207.090423_builder_junos_182_r2]
JUNOS qfx platform support [20181207.090423_builder_junos_182_r2]
JUNOS dcp network modules [20181207.090423_builder_junos_182_r2]
JUNOS modules [20181207.090423_builder_junos_182_r2]
JUNOS qfx modules [20181207.090423_builder_junos_182_r2]
JUNOS qfx Data Plane Crypto Support [20181207.090423_builder_junos_182_r2]
JUNOS daemons [20181207.090423_builder_junos_182_r2]
JUNOS qfx daemons [20181207.090423_builder_junos_182_r2]
JUNOS Services URL Filter package [20181207.090423_builder_junos_182_r2]
JUNOS Services TLB Service PIC package [20181207.090423_builder_junos_182_r2]
JUNOS Services Telemetry [20181207.090423_builder_junos_182_r2]
JUNOS Services SSL [20181207.090423_builder_junos_182_r2]
JUNOS Services SOFTWIRE [20181207.090423_builder_junos_182_r2]
JUNOS Services Stateful Firewall [20181207.090423_builder_junos_182_r2]
JUNOS Services RPM [20181207.090423_builder_junos_182_r2]
JUNOS Services PCEF package [20181207.090423_builder_junos_182_r2]
JUNOS Services NAT [20181207.090423_builder_junos_182_r2]
JUNOS Services Mobile Subscriber Service Container package [20181207.090423_builder_junos_182_r2]
JUNOS Services MobileNext Software package [20181207.090423_builder_junos_182_r2]
JUNOS Services Logging Report Framework package [20181207.090423_builder_junos_182_r2]
JUNOS Services LL-PDF Container package [20181207.090423_builder_junos_182_r2]
JUNOS Services Jflow Container package [20181207.090423_builder_junos_182_r2]
JUNOS Services Deep Packet Inspection package [20181207.090423_builder_junos_182_r2]
JUNOS Services IPSec [20181207.090423_builder_junos_182_r2]
JUNOS Services IDS [20181207.090423_builder_junos_182_r2]
JUNOS IDP Services [20181207.090423_builder_junos_182_r2]
JUNOS Services HTTP Content Management package [20181207.090423_builder_junos_182_r2]
JUNOS Services Flowd MS-MPC Software package [20181207.090423_builder_junos_182_r2]
JUNOS Services Crypto [20181207.090423_builder_junos_182_r2]
JUNOS Services Captive Portal and Content Delivery Container package [20181207.090423_builder_junos_182_r2]
JUNOS Services COS [20181207.090423_builder_junos_182_r2]
JUNOS AppId Services [20181207.090423_builder_junos_182_r2]
JUNOS Services Application Level Gateways [20181207.090423_builder_junos_182_r2]
JUNOS Services AACL Container package [20181207.090423_builder_junos_182_r2]
JUNOS SDN Software Suite [20181207.090423_builder_junos_182_r2]
JUNOS Extension Toolkit [20181207.090423_builder_junos_182_r2]
JUNOS Packet Forwarding Engine Support (DC-PFE) [20181207.090423_builder_junos_182_r2]
JUNOS Packet Forwarding Engine Support (M/T Common) [20181207.090423_builder_junos_182_r2]
JUNOS J-Insight [20181207.090423_builder_junos_182_r2]
JUNOS jfirmware [20181207.090423_builder_junos_182_r2]
JUNOS Online Documentation [20181207.090423_builder_junos_182_r2]
JUNOS jail runtime [20181108.217da31_builder_stable_11]
JUNOS FIPS mode utilities [20181207.090423_builder_junos_182_r2]
JUNOS Host Software [3.14.64-rt67-WR7.0.0.26_ovp:3.1.0]
JUNOS Host qfx-10-m platform package [18.2R2.6]
JUNOS Host qfx-10-m fabric package [18.2R2.6]
JUNOS Host qfx-10-m data-plane package [18.2R2.6]
JUNOS Host qfx-10-m base package [18.2R2.6]
JUNOS Host qfx-10-m control-plane package [18.2R2.6]

{master}
    """
    result = [{'interface': 'et-0/0/0', 'state': 'up'},
              {'interface': 'et-0/0/0.0', 'state': 'up'},
              {'interface': 'gr-0/0/0', 'state': 'up'},
              {'interface': 'pfe-0/0/0', 'state': 'up'},
              {'interface': 'pfe-0/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-0/0/0', 'state': 'up'},
              {'interface': 'pfh-0/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-0/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-0/0/0', 'state': 'up'},
              {'interface': 'et-0/0/1', 'state': 'up'},
              {'interface': 'et-0/0/1.0', 'state': 'up'},
              {'interface': 'sxe-0/0/1', 'state': 'up'},
              {'interface': 'et-0/0/2', 'state': 'up'},
              {'interface': 'et-0/0/2.0', 'state': 'up'},
              {'interface': 'sxe-0/0/2', 'state': 'up'},
              {'interface': 'et-0/0/3', 'state': 'up'},
              {'interface': 'et-0/0/3.0', 'state': 'up'},
              {'interface': 'sxe-0/0/3', 'state': 'up'},
              {'interface': 'et-0/0/4', 'state': 'up'},
              {'interface': 'et-0/0/4.0', 'state': 'up'},
              {'interface': 'sxe-0/0/4', 'state': 'up'},
              {'interface': 'et-0/0/5', 'state': 'up'},
              {'interface': 'et-0/0/5.0', 'state': 'up'},
              {'interface': 'sxe-0/0/5', 'state': 'up'},
              {'interface': 'et-0/0/6', 'state': 'up'},
              {'interface': 'et-0/0/6.0', 'state': 'up'},
              {'interface': 'et-0/0/7', 'state': 'up'},
              {'interface': 'et-0/0/7.0', 'state': 'up'},
              {'interface': 'et-0/0/8', 'state': 'up'},
              {'interface': 'et-0/0/8.0', 'state': 'up'},
              {'interface': 'et-0/0/9', 'state': 'up'},
              {'interface': 'et-0/0/9.0', 'state': 'up'},
              {'interface': 'et-0/0/10', 'state': 'up'},
              {'interface': 'et-0/0/10.0', 'state': 'up'},
              {'interface': 'et-0/0/11', 'state': 'up'},
              {'interface': 'et-0/0/11.0', 'state': 'up'},
              {'interface': 'et-0/0/12', 'state': 'up'},
              {'interface': 'et-0/0/12.3000', 'state': 'up'},
              {'interface': 'et-0/0/12.32767', 'state': 'up'},
              {'interface': 'et-0/0/13', 'state': 'down'},
              {'interface': 'et-0/0/13.0', 'state': 'down'},
              {'interface': 'et-0/0/14', 'state': 'up'},
              {'interface': 'et-0/0/14.3000', 'state': 'up'},
              {'interface': 'et-0/0/14.32767', 'state': 'up'},
              {'interface': 'et-0/0/15', 'state': 'up'},
              {'interface': 'et-0/0/15.3000', 'state': 'up'},
              {'interface': 'et-0/0/15.32767', 'state': 'up'},
              {'interface': 'et-0/0/16', 'state': 'up'},
              {'interface': 'et-0/0/16.3000', 'state': 'up'},
              {'interface': 'et-0/0/16.32767', 'state': 'up'},
              {'interface': 'et-0/0/17', 'state': 'down'},
              {'interface': 'et-0/0/17.0', 'state': 'down'},
              {'interface': 'et-0/0/18', 'state': 'up'},
              {'interface': 'et-0/0/18.0', 'state': 'up'},
              {'interface': 'et-0/0/19', 'state': 'up'},
              {'interface': 'et-0/0/19.0', 'state': 'up'},
              {'interface': 'et-0/0/20', 'state': 'up'},
              {'interface': 'et-0/0/20.0', 'state': 'up'},
              {'interface': 'et-0/0/21', 'state': 'up'},
              {'interface': 'et-0/0/21.0', 'state': 'up'},
              {'interface': 'et-0/0/22', 'state': 'up'},
              {'interface': 'et-0/0/22.0', 'state': 'up'},
              {'interface': 'et-0/0/23', 'state': 'up'},
              {'interface': 'et-0/0/23.0', 'state': 'up'},
              {'interface': 'et-0/0/24', 'state': 'up'},
              {'interface': 'et-0/0/24.0', 'state': 'up'},
              {'interface': 'et-0/0/25', 'state': 'up'},
              {'interface': 'et-0/0/25.0', 'state': 'up'},
              {'interface': 'et-0/0/26', 'state': 'up'},
              {'interface': 'et-0/0/26.0', 'state': 'up'},
              {'interface': 'et-0/0/27', 'state': 'up'},
              {'interface': 'et-0/0/27.0', 'state': 'up'},
              {'interface': 'et-0/0/28', 'state': 'up'},
              {'interface': 'et-0/0/28.0', 'state': 'up'},
              {'interface': 'et-0/0/29', 'state': 'up'},
              {'interface': 'et-0/0/29.0', 'state': 'up'},
              {'interface': 'et-1/0/0', 'state': 'up'},
              {'interface': 'et-1/0/0.0', 'state': 'up'},
              {'interface': 'pfe-1/0/0', 'state': 'up'},
              {'interface': 'pfe-1/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-1/0/0', 'state': 'up'},
              {'interface': 'pfh-1/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-1/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-1/0/0', 'state': 'up'},
              {'interface': 'et-1/0/1', 'state': 'up'},
              {'interface': 'et-1/0/1.0', 'state': 'up'},
              {'interface': 'sxe-1/0/1', 'state': 'up'},
              {'interface': 'et-1/0/2', 'state': 'up'},
              {'interface': 'et-1/0/2.0', 'state': 'up'},
              {'interface': 'sxe-1/0/2', 'state': 'up'},
              {'interface': 'et-1/0/3', 'state': 'up'},
              {'interface': 'et-1/0/3.0', 'state': 'up'},
              {'interface': 'sxe-1/0/3', 'state': 'up'},
              {'interface': 'et-1/0/4', 'state': 'up'},
              {'interface': 'et-1/0/4.0', 'state': 'up'},
              {'interface': 'sxe-1/0/4', 'state': 'up'},
              {'interface': 'et-1/0/5', 'state': 'up'},
              {'interface': 'et-1/0/5.0', 'state': 'up'},
              {'interface': 'sxe-1/0/5', 'state': 'up'},
              {'interface': 'et-1/0/6', 'state': 'up'},
              {'interface': 'et-1/0/6.0', 'state': 'up'},
              {'interface': 'et-1/0/7', 'state': 'up'},
              {'interface': 'et-1/0/7.0', 'state': 'up'},
              {'interface': 'et-1/0/8', 'state': 'up'},
              {'interface': 'et-1/0/8.0', 'state': 'up'},
              {'interface': 'et-1/0/9', 'state': 'up'},
              {'interface': 'et-1/0/9.0', 'state': 'up'},
              {'interface': 'et-1/0/10', 'state': 'up'},
              {'interface': 'et-1/0/10.0', 'state': 'up'},
              {'interface': 'et-1/0/11', 'state': 'up'},
              {'interface': 'et-1/0/11.0', 'state': 'up'},
              {'interface': 'et-1/0/12', 'state': 'down'},
              {'interface': 'et-1/0/12.0', 'state': 'down'},
              {'interface': 'et-1/0/13', 'state': 'up'},
              {'interface': 'et-1/0/13.3000', 'state': 'up'},
              {'interface': 'et-1/0/13.32767', 'state': 'up'},
              {'interface': 'et-1/0/14', 'state': 'down'},
              {'interface': 'et-1/0/14.0', 'state': 'down'},
              {'interface': 'et-1/0/15', 'state': 'down'},
              {'interface': 'et-1/0/15.3000', 'state': 'down'},
              {'interface': 'et-1/0/15.32767', 'state': 'down'},
              {'interface': 'et-1/0/16', 'state': 'up'},
              {'interface': 'et-1/0/16.3000', 'state': 'up'},
              {'interface': 'et-1/0/16.32767', 'state': 'up'},
              {'interface': 'et-1/0/17', 'state': 'up'},
              {'interface': 'et-1/0/17.3000', 'state': 'up'},
              {'interface': 'et-1/0/17.32767', 'state': 'up'},
              {'interface': 'et-1/0/18', 'state': 'up'},
              {'interface': 'et-1/0/18.0', 'state': 'up'},
              {'interface': 'et-1/0/19', 'state': 'up'},
              {'interface': 'et-1/0/19.0', 'state': 'up'},
              {'interface': 'et-1/0/20', 'state': 'up'},
              {'interface': 'et-1/0/20.0', 'state': 'up'},
              {'interface': 'et-1/0/21', 'state': 'up'},
              {'interface': 'et-1/0/21.0', 'state': 'up'},
              {'interface': 'et-1/0/22', 'state': 'up'},
              {'interface': 'et-1/0/22.0', 'state': 'up'},
              {'interface': 'et-1/0/23', 'state': 'up'},
              {'interface': 'et-1/0/23.0', 'state': 'up'},
              {'interface': 'et-1/0/24', 'state': 'up'},
              {'interface': 'et-1/0/24.0', 'state': 'up'},
              {'interface': 'et-1/0/25', 'state': 'up'},
              {'interface': 'et-1/0/25.0', 'state': 'up'},
              {'interface': 'et-1/0/26', 'state': 'up'},
              {'interface': 'et-1/0/26.0', 'state': 'up'},
              {'interface': 'et-1/0/27', 'state': 'up'},
              {'interface': 'et-1/0/27.0', 'state': 'up'},
              {'interface': 'et-1/0/28', 'state': 'up'},
              {'interface': 'et-1/0/28.0', 'state': 'up'},
              {'interface': 'et-1/0/29', 'state': 'up'},
              {'interface': 'et-1/0/29.0', 'state': 'up'},
              {'interface': 'et-2/0/0', 'state': 'up'},
              {'interface': 'et-2/0/0.0', 'state': 'up'},
              {'interface': 'pfe-2/0/0', 'state': 'up'},
              {'interface': 'pfe-2/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-2/0/0', 'state': 'up'},
              {'interface': 'pfh-2/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-2/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-2/0/0', 'state': 'up'},
              {'interface': 'et-2/0/1', 'state': 'up'},
              {'interface': 'et-2/0/1.0', 'state': 'up'},
              {'interface': 'sxe-2/0/1', 'state': 'up'},
              {'interface': 'et-2/0/2', 'state': 'up'},
              {'interface': 'et-2/0/2.0', 'state': 'up'},
              {'interface': 'sxe-2/0/2', 'state': 'up'},
              {'interface': 'et-2/0/3', 'state': 'up'},
              {'interface': 'et-2/0/3.0', 'state': 'up'},
              {'interface': 'sxe-2/0/3', 'state': 'up'},
              {'interface': 'et-2/0/4', 'state': 'up'},
              {'interface': 'et-2/0/4.0', 'state': 'up'},
              {'interface': 'sxe-2/0/4', 'state': 'up'},
              {'interface': 'et-2/0/5', 'state': 'up'},
              {'interface': 'et-2/0/5.0', 'state': 'up'},
              {'interface': 'sxe-2/0/5', 'state': 'up'},
              {'interface': 'et-2/0/6', 'state': 'up'},
              {'interface': 'et-2/0/6.0', 'state': 'up'},
              {'interface': 'et-2/0/7', 'state': 'up'},
              {'interface': 'et-2/0/7.0', 'state': 'up'},
              {'interface': 'et-2/0/8', 'state': 'up'},
              {'interface': 'et-2/0/8.0', 'state': 'up'},
              {'interface': 'et-2/0/9', 'state': 'up'},
              {'interface': 'et-2/0/9.0', 'state': 'up'},
              {'interface': 'et-2/0/10', 'state': 'up'},
              {'interface': 'et-2/0/10.0', 'state': 'up'},
              {'interface': 'et-2/0/11', 'state': 'up'},
              {'interface': 'et-2/0/11.0', 'state': 'up'},
              {'interface': 'et-2/0/12', 'state': 'up'},
              {'interface': 'et-2/0/12.3000', 'state': 'up'},
              {'interface': 'et-2/0/12.32767', 'state': 'up'},
              {'interface': 'et-2/0/13', 'state': 'up'},
              {'interface': 'et-2/0/13.3000', 'state': 'up'},
              {'interface': 'et-2/0/13.32767', 'state': 'up'},
              {'interface': 'et-2/0/14', 'state': 'up'},
              {'interface': 'et-2/0/14.3000', 'state': 'up'},
              {'interface': 'et-2/0/14.32767', 'state': 'up'},
              {'interface': 'et-2/0/15', 'state': 'up'},
              {'interface': 'et-2/0/15.3000', 'state': 'up'},
              {'interface': 'et-2/0/15.32767', 'state': 'up'},
              {'interface': 'et-2/0/16', 'state': 'up'},
              {'interface': 'et-2/0/16.3000', 'state': 'up'},
              {'interface': 'et-2/0/16.32767', 'state': 'up'},
              {'interface': 'et-2/0/17', 'state': 'up'},
              {'interface': 'et-2/0/17.3000', 'state': 'up'},
              {'interface': 'et-2/0/17.32767', 'state': 'up'},
              {'interface': 'et-2/0/18', 'state': 'up'},
              {'interface': 'et-2/0/18.0', 'state': 'up'},
              {'interface': 'et-2/0/19', 'state': 'up'},
              {'interface': 'et-2/0/19.0', 'state': 'up'},
              {'interface': 'et-2/0/20', 'state': 'up'},
              {'interface': 'et-2/0/20.0', 'state': 'up'},
              {'interface': 'et-2/0/21', 'state': 'up'},
              {'interface': 'et-2/0/21.0', 'state': 'up'},
              {'interface': 'et-2/0/22', 'state': 'up'},
              {'interface': 'et-2/0/22.0', 'state': 'up'},
              {'interface': 'et-2/0/23', 'state': 'up'},
              {'interface': 'et-2/0/23.0', 'state': 'up'},
              {'interface': 'et-2/0/24', 'state': 'up'},
              {'interface': 'et-2/0/24.0', 'state': 'up'},
              {'interface': 'et-2/0/25', 'state': 'up'},
              {'interface': 'et-2/0/25.0', 'state': 'up'},
              {'interface': 'et-2/0/26', 'state': 'up'},
              {'interface': 'et-2/0/26.0', 'state': 'up'},
              {'interface': 'et-2/0/27', 'state': 'up'},
              {'interface': 'et-2/0/27.0', 'state': 'up'},
              {'interface': 'et-2/0/28', 'state': 'up'},
              {'interface': 'et-2/0/28.0', 'state': 'up'},
              {'interface': 'et-2/0/29', 'state': 'up'},
              {'interface': 'et-2/0/29.0', 'state': 'up'},
              {'interface': 'et-3/0/0', 'state': 'up'},
              {'interface': 'et-3/0/0.0', 'state': 'up'},
              {'interface': 'pfe-3/0/0', 'state': 'up'},
              {'interface': 'pfe-3/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-3/0/0', 'state': 'up'},
              {'interface': 'pfh-3/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-3/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-3/0/0', 'state': 'up'},
              {'interface': 'et-3/0/1', 'state': 'up'},
              {'interface': 'et-3/0/1.0', 'state': 'up'},
              {'interface': 'sxe-3/0/1', 'state': 'up'},
              {'interface': 'et-3/0/2', 'state': 'up'},
              {'interface': 'et-3/0/2.0', 'state': 'up'},
              {'interface': 'sxe-3/0/2', 'state': 'up'},
              {'interface': 'et-3/0/3', 'state': 'up'},
              {'interface': 'et-3/0/3.0', 'state': 'up'},
              {'interface': 'sxe-3/0/3', 'state': 'up'},
              {'interface': 'et-3/0/4', 'state': 'up'},
              {'interface': 'et-3/0/4.0', 'state': 'up'},
              {'interface': 'sxe-3/0/4', 'state': 'up'},
              {'interface': 'et-3/0/5', 'state': 'up'},
              {'interface': 'et-3/0/5.0', 'state': 'up'},
              {'interface': 'sxe-3/0/5', 'state': 'up'},
              {'interface': 'et-3/0/6', 'state': 'up'},
              {'interface': 'et-3/0/6.0', 'state': 'up'},
              {'interface': 'et-3/0/7', 'state': 'up'},
              {'interface': 'et-3/0/7.0', 'state': 'up'},
              {'interface': 'et-3/0/8', 'state': 'up'},
              {'interface': 'et-3/0/8.0', 'state': 'up'},
              {'interface': 'et-3/0/9', 'state': 'up'},
              {'interface': 'et-3/0/9.0', 'state': 'up'},
              {'interface': 'et-3/0/10', 'state': 'up'},
              {'interface': 'et-3/0/10.0', 'state': 'up'},
              {'interface': 'et-3/0/11', 'state': 'up'},
              {'interface': 'et-3/0/11.0', 'state': 'up'},
              {'interface': 'et-3/0/12', 'state': 'up'},
              {'interface': 'et-3/0/12.3000', 'state': 'up'},
              {'interface': 'et-3/0/12.32767', 'state': 'up'},
              {'interface': 'et-3/0/13', 'state': 'up'},
              {'interface': 'et-3/0/13.3000', 'state': 'up'},
              {'interface': 'et-3/0/13.32767', 'state': 'up'},
              {'interface': 'et-3/0/14', 'state': 'up'},
              {'interface': 'et-3/0/14.3000', 'state': 'up'},
              {'interface': 'et-3/0/14.32767', 'state': 'up'},
              {'interface': 'et-3/0/15', 'state': 'up'},
              {'interface': 'et-3/0/15.3000', 'state': 'up'},
              {'interface': 'et-3/0/15.32767', 'state': 'up'},
              {'interface': 'et-3/0/16', 'state': 'up'},
              {'interface': 'et-3/0/16.3000', 'state': 'up'},
              {'interface': 'et-3/0/16.32767', 'state': 'up'},
              {'interface': 'et-3/0/17', 'state': 'down'},
              {'interface': 'et-3/0/17.0', 'state': 'down'},
              {'interface': 'et-3/0/18', 'state': 'up'},
              {'interface': 'et-3/0/18.0', 'state': 'up'},
              {'interface': 'et-3/0/19', 'state': 'up'},
              {'interface': 'et-3/0/19.0', 'state': 'up'},
              {'interface': 'et-3/0/20', 'state': 'up'},
              {'interface': 'et-3/0/20.0', 'state': 'up'},
              {'interface': 'et-3/0/21', 'state': 'up'},
              {'interface': 'et-3/0/21.0', 'state': 'up'},
              {'interface': 'et-3/0/22', 'state': 'up'},
              {'interface': 'et-3/0/22.0', 'state': 'up'},
              {'interface': 'et-3/0/23', 'state': 'up'},
              {'interface': 'et-3/0/23.0', 'state': 'up'},
              {'interface': 'et-3/0/24', 'state': 'up'},
              {'interface': 'et-3/0/24.0', 'state': 'up'},
              {'interface': 'et-3/0/25', 'state': 'up'},
              {'interface': 'et-3/0/25.0', 'state': 'up'},
              {'interface': 'et-3/0/26', 'state': 'up'},
              {'interface': 'et-3/0/26.0', 'state': 'up'},
              {'interface': 'et-3/0/27', 'state': 'up'},
              {'interface': 'et-3/0/27.0', 'state': 'up'},
              {'interface': 'et-3/0/28', 'state': 'up'},
              {'interface': 'et-3/0/28.0', 'state': 'up'},
              {'interface': 'et-3/0/29', 'state': 'up'},
              {'interface': 'et-3/0/29.0', 'state': 'up'},
              {'interface': 'et-4/0/0', 'state': 'up'},
              {'interface': 'et-4/0/0.0', 'state': 'up'},
              {'interface': 'pfe-4/0/0', 'state': 'up'},
              {'interface': 'pfe-4/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-4/0/0', 'state': 'up'},
              {'interface': 'pfh-4/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-4/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-4/0/0', 'state': 'up'},
              {'interface': 'et-4/0/1', 'state': 'up'},
              {'interface': 'et-4/0/1.0', 'state': 'up'},
              {'interface': 'sxe-4/0/1', 'state': 'up'},
              {'interface': 'et-4/0/2', 'state': 'up'},
              {'interface': 'et-4/0/2.0', 'state': 'up'},
              {'interface': 'sxe-4/0/2', 'state': 'up'},
              {'interface': 'et-4/0/3', 'state': 'up'},
              {'interface': 'et-4/0/3.0', 'state': 'up'},
              {'interface': 'sxe-4/0/3', 'state': 'up'},
              {'interface': 'et-4/0/4', 'state': 'up'},
              {'interface': 'et-4/0/4.0', 'state': 'up'},
              {'interface': 'sxe-4/0/4', 'state': 'up'},
              {'interface': 'et-4/0/5', 'state': 'up'},
              {'interface': 'et-4/0/5.0', 'state': 'up'},
              {'interface': 'sxe-4/0/5', 'state': 'up'},
              {'interface': 'et-4/0/6', 'state': 'up'},
              {'interface': 'et-4/0/6.0', 'state': 'up'},
              {'interface': 'et-4/0/7', 'state': 'up'},
              {'interface': 'et-4/0/7.0', 'state': 'up'},
              {'interface': 'et-4/0/8', 'state': 'up'},
              {'interface': 'et-4/0/8.0', 'state': 'up'},
              {'interface': 'et-4/0/9', 'state': 'up'},
              {'interface': 'et-4/0/9.0', 'state': 'up'},
              {'interface': 'et-4/0/10', 'state': 'up'},
              {'interface': 'et-4/0/10.0', 'state': 'up'},
              {'interface': 'et-4/0/11', 'state': 'up'},
              {'interface': 'et-4/0/11.0', 'state': 'up'},
              {'interface': 'et-4/0/12', 'state': 'up'},
              {'interface': 'et-4/0/12.3000', 'state': 'up'},
              {'interface': 'et-4/0/12.32767', 'state': 'up'},
              {'interface': 'et-4/0/13', 'state': 'up'},
              {'interface': 'et-4/0/13.3000', 'state': 'up'},
              {'interface': 'et-4/0/13.32767', 'state': 'up'},
              {'interface': 'et-4/0/14', 'state': 'up'},
              {'interface': 'et-4/0/14.3000', 'state': 'up'},
              {'interface': 'et-4/0/14.32767', 'state': 'up'},
              {'interface': 'et-4/0/15', 'state': 'up'},
              {'interface': 'et-4/0/15.3000', 'state': 'up'},
              {'interface': 'et-4/0/15.32767', 'state': 'up'},
              {'interface': 'et-4/0/16', 'state': 'up'},
              {'interface': 'et-4/0/16.3000', 'state': 'up'},
              {'interface': 'et-4/0/16.32767', 'state': 'up'},
              {'interface': 'et-4/0/17', 'state': 'up'},
              {'interface': 'et-4/0/17.3000', 'state': 'up'},
              {'interface': 'et-4/0/17.32767', 'state': 'up'},
              {'interface': 'et-4/0/18', 'state': 'up'},
              {'interface': 'et-4/0/18.0', 'state': 'up'},
              {'interface': 'et-4/0/19', 'state': 'up'},
              {'interface': 'et-4/0/19.0', 'state': 'up'},
              {'interface': 'et-4/0/20', 'state': 'up'},
              {'interface': 'et-4/0/20.0', 'state': 'up'},
              {'interface': 'et-4/0/21', 'state': 'up'},
              {'interface': 'et-4/0/21.0', 'state': 'up'},
              {'interface': 'et-4/0/22', 'state': 'up'},
              {'interface': 'et-4/0/22.0', 'state': 'up'},
              {'interface': 'et-4/0/23', 'state': 'up'},
              {'interface': 'et-4/0/23.0', 'state': 'up'},
              {'interface': 'et-4/0/24', 'state': 'up'},
              {'interface': 'et-4/0/24.0', 'state': 'up'},
              {'interface': 'et-4/0/25', 'state': 'up'},
              {'interface': 'et-4/0/25.0', 'state': 'up'},
              {'interface': 'et-4/0/26', 'state': 'up'},
              {'interface': 'et-4/0/26.0', 'state': 'up'},
              {'interface': 'et-4/0/27', 'state': 'up'},
              {'interface': 'et-4/0/27.0', 'state': 'up'},
              {'interface': 'et-4/0/28', 'state': 'up'},
              {'interface': 'et-4/0/28.0', 'state': 'up'},
              {'interface': 'et-4/0/29', 'state': 'up'},
              {'interface': 'et-4/0/29.0', 'state': 'up'},
              {'interface': 'et-5/0/0', 'state': 'up'},
              {'interface': 'et-5/0/0.0', 'state': 'up'},
              {'interface': 'pfe-5/0/0', 'state': 'up'},
              {'interface': 'pfe-5/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-5/0/0', 'state': 'up'},
              {'interface': 'pfh-5/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-5/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-5/0/0', 'state': 'up'},
              {'interface': 'et-5/0/1', 'state': 'up'},
              {'interface': 'et-5/0/1.0', 'state': 'up'},
              {'interface': 'sxe-5/0/1', 'state': 'up'},
              {'interface': 'et-5/0/2', 'state': 'up'},
              {'interface': 'et-5/0/2.0', 'state': 'up'},
              {'interface': 'sxe-5/0/2', 'state': 'up'},
              {'interface': 'et-5/0/3', 'state': 'up'},
              {'interface': 'et-5/0/3.0', 'state': 'up'},
              {'interface': 'sxe-5/0/3', 'state': 'up'},
              {'interface': 'et-5/0/4', 'state': 'up'},
              {'interface': 'et-5/0/4.0', 'state': 'up'},
              {'interface': 'sxe-5/0/4', 'state': 'up'},
              {'interface': 'et-5/0/5', 'state': 'up'},
              {'interface': 'et-5/0/5.0', 'state': 'up'},
              {'interface': 'sxe-5/0/5', 'state': 'up'},
              {'interface': 'et-5/0/6', 'state': 'up'},
              {'interface': 'et-5/0/6.0', 'state': 'up'},
              {'interface': 'et-5/0/7', 'state': 'up'},
              {'interface': 'et-5/0/7.0', 'state': 'up'},
              {'interface': 'et-5/0/8', 'state': 'up'},
              {'interface': 'et-5/0/8.0', 'state': 'up'},
              {'interface': 'et-5/0/9', 'state': 'up'},
              {'interface': 'et-5/0/9.0', 'state': 'up'},
              {'interface': 'et-5/0/10', 'state': 'up'},
              {'interface': 'et-5/0/10.0', 'state': 'up'},
              {'interface': 'et-5/0/11', 'state': 'up'},
              {'interface': 'et-5/0/11.0', 'state': 'up'},
              {'interface': 'et-5/0/12', 'state': 'down'},
              {'interface': 'et-5/0/12.0', 'state': 'down'},
              {'interface': 'et-5/0/13', 'state': 'up'},
              {'interface': 'et-5/0/13.3000', 'state': 'up'},
              {'interface': 'et-5/0/13.32767', 'state': 'up'},
              {'interface': 'et-5/0/14', 'state': 'up'},
              {'interface': 'et-5/0/14.3000', 'state': 'up'},
              {'interface': 'et-5/0/14.32767', 'state': 'up'},
              {'interface': 'et-5/0/15', 'state': 'up'},
              {'interface': 'et-5/0/15.3000', 'state': 'up'},
              {'interface': 'et-5/0/15.32767', 'state': 'up'},
              {'interface': 'et-5/0/16', 'state': 'down'},
              {'interface': 'et-5/0/16.0', 'state': 'down'},
              {'interface': 'et-5/0/17', 'state': 'down'},
              {'interface': 'et-5/0/17.0', 'state': 'down'},
              {'interface': 'et-5/0/18', 'state': 'up'},
              {'interface': 'et-5/0/18.0', 'state': 'up'},
              {'interface': 'et-5/0/19', 'state': 'up'},
              {'interface': 'et-5/0/19.0', 'state': 'up'},
              {'interface': 'et-5/0/20', 'state': 'up'},
              {'interface': 'et-5/0/20.0', 'state': 'up'},
              {'interface': 'et-5/0/21', 'state': 'up'},
              {'interface': 'et-5/0/21.0', 'state': 'up'},
              {'interface': 'et-5/0/22', 'state': 'up'},
              {'interface': 'et-5/0/22.0', 'state': 'up'},
              {'interface': 'et-5/0/23', 'state': 'up'},
              {'interface': 'et-5/0/23.0', 'state': 'up'},
              {'interface': 'et-5/0/24', 'state': 'up'},
              {'interface': 'et-5/0/24.0', 'state': 'up'},
              {'interface': 'et-5/0/25', 'state': 'up'},
              {'interface': 'et-5/0/25.0', 'state': 'up'},
              {'interface': 'et-5/0/26', 'state': 'up'},
              {'interface': 'et-5/0/26.0', 'state': 'up'},
              {'interface': 'et-5/0/27', 'state': 'up'},
              {'interface': 'et-5/0/27.0', 'state': 'up'},
              {'interface': 'et-5/0/28', 'state': 'up'},
              {'interface': 'et-5/0/28.0', 'state': 'up'},
              {'interface': 'et-5/0/29', 'state': 'up'},
              {'interface': 'et-5/0/29.0', 'state': 'up'},
              {'interface': 'et-6/0/0', 'state': 'up'},
              {'interface': 'et-6/0/0.0', 'state': 'up'},
              {'interface': 'pfe-6/0/0', 'state': 'up'},
              {'interface': 'pfe-6/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-6/0/0', 'state': 'up'},
              {'interface': 'pfh-6/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-6/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-6/0/0', 'state': 'up'},
              {'interface': 'et-6/0/1', 'state': 'up'},
              {'interface': 'et-6/0/1.0', 'state': 'up'},
              {'interface': 'sxe-6/0/1', 'state': 'up'},
              {'interface': 'et-6/0/2', 'state': 'up'},
              {'interface': 'et-6/0/2.0', 'state': 'up'},
              {'interface': 'sxe-6/0/2', 'state': 'up'},
              {'interface': 'et-6/0/3', 'state': 'up'},
              {'interface': 'et-6/0/3.0', 'state': 'up'},
              {'interface': 'sxe-6/0/3', 'state': 'up'},
              {'interface': 'et-6/0/4', 'state': 'up'},
              {'interface': 'et-6/0/4.0', 'state': 'up'},
              {'interface': 'sxe-6/0/4', 'state': 'up'},
              {'interface': 'et-6/0/5', 'state': 'up'},
              {'interface': 'et-6/0/5.0', 'state': 'up'},
              {'interface': 'sxe-6/0/5', 'state': 'up'},
              {'interface': 'et-6/0/6', 'state': 'up'},
              {'interface': 'et-6/0/6.0', 'state': 'up'},
              {'interface': 'et-6/0/7', 'state': 'up'},
              {'interface': 'et-6/0/7.0', 'state': 'up'},
              {'interface': 'et-6/0/8', 'state': 'up'},
              {'interface': 'et-6/0/8.0', 'state': 'up'},
              {'interface': 'et-6/0/9', 'state': 'up'},
              {'interface': 'et-6/0/9.0', 'state': 'up'},
              {'interface': 'et-6/0/10', 'state': 'up'},
              {'interface': 'et-6/0/10.0', 'state': 'up'},
              {'interface': 'et-6/0/11', 'state': 'up'},
              {'interface': 'et-6/0/11.0', 'state': 'up'},
              {'interface': 'et-6/0/12', 'state': 'up'},
              {'interface': 'et-6/0/12.3000', 'state': 'up'},
              {'interface': 'et-6/0/12.32767', 'state': 'up'},
              {'interface': 'et-6/0/13', 'state': 'up'},
              {'interface': 'et-6/0/13.3000', 'state': 'up'},
              {'interface': 'et-6/0/13.32767', 'state': 'up'},
              {'interface': 'et-6/0/14', 'state': 'up'},
              {'interface': 'et-6/0/14.3000', 'state': 'up'},
              {'interface': 'et-6/0/14.32767', 'state': 'up'},
              {'interface': 'et-6/0/15', 'state': 'down'},
              {'interface': 'et-6/0/15.0', 'state': 'down'},
              {'interface': 'et-6/0/16', 'state': 'up'},
              {'interface': 'et-6/0/16.3000', 'state': 'up'},
              {'interface': 'et-6/0/16.32767', 'state': 'up'},
              {'interface': 'et-6/0/17', 'state': 'up'},
              {'interface': 'et-6/0/17.3000', 'state': 'up'},
              {'interface': 'et-6/0/17.32767', 'state': 'up'},
              {'interface': 'et-6/0/18', 'state': 'up'},
              {'interface': 'et-6/0/18.0', 'state': 'up'},
              {'interface': 'et-6/0/19', 'state': 'down'},
              {'interface': 'et-6/0/19.0', 'state': 'down'},
              {'interface': 'et-6/0/20', 'state': 'up'},
              {'interface': 'et-6/0/20.0', 'state': 'up'},
              {'interface': 'et-6/0/21', 'state': 'up'},
              {'interface': 'et-6/0/21.0', 'state': 'up'},
              {'interface': 'et-6/0/22', 'state': 'up'},
              {'interface': 'et-6/0/22.0', 'state': 'up'},
              {'interface': 'et-6/0/23', 'state': 'up'},
              {'interface': 'et-6/0/23.0', 'state': 'up'},
              {'interface': 'et-6/0/24', 'state': 'up'},
              {'interface': 'et-6/0/24.0', 'state': 'up'},
              {'interface': 'et-6/0/25', 'state': 'up'},
              {'interface': 'et-6/0/25.0', 'state': 'up'},
              {'interface': 'et-6/0/26', 'state': 'up'},
              {'interface': 'et-6/0/26.0', 'state': 'up'},
              {'interface': 'et-6/0/27', 'state': 'up'},
              {'interface': 'et-6/0/27.0', 'state': 'up'},
              {'interface': 'et-6/0/28', 'state': 'up'},
              {'interface': 'et-6/0/28.0', 'state': 'up'},
              {'interface': 'et-6/0/29', 'state': 'up'},
              {'interface': 'et-6/0/29.0', 'state': 'up'},
              {'interface': 'et-7/0/0', 'state': 'up'},
              {'interface': 'et-7/0/0.0', 'state': 'up'},
              {'interface': 'pfe-7/0/0', 'state': 'up'},
              {'interface': 'pfe-7/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-7/0/0', 'state': 'up'},
              {'interface': 'pfh-7/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-7/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-7/0/0', 'state': 'up'},
              {'interface': 'et-7/0/1', 'state': 'up'},
              {'interface': 'et-7/0/1.0', 'state': 'up'},
              {'interface': 'sxe-7/0/1', 'state': 'up'},
              {'interface': 'et-7/0/2', 'state': 'up'},
              {'interface': 'et-7/0/2.0', 'state': 'up'},
              {'interface': 'sxe-7/0/2', 'state': 'up'},
              {'interface': 'et-7/0/3', 'state': 'up'},
              {'interface': 'et-7/0/3.0', 'state': 'up'},
              {'interface': 'sxe-7/0/3', 'state': 'up'},
              {'interface': 'et-7/0/4', 'state': 'up'},
              {'interface': 'et-7/0/4.0', 'state': 'up'},
              {'interface': 'sxe-7/0/4', 'state': 'up'},
              {'interface': 'et-7/0/5', 'state': 'up'},
              {'interface': 'et-7/0/5.0', 'state': 'up'},
              {'interface': 'sxe-7/0/5', 'state': 'up'},
              {'interface': 'et-7/0/6', 'state': 'up'},
              {'interface': 'et-7/0/6.0', 'state': 'up'},
              {'interface': 'et-7/0/7', 'state': 'up'},
              {'interface': 'et-7/0/7.0', 'state': 'up'},
              {'interface': 'et-7/0/8', 'state': 'up'},
              {'interface': 'et-7/0/8.0', 'state': 'up'},
              {'interface': 'et-7/0/9', 'state': 'up'},
              {'interface': 'et-7/0/9.0', 'state': 'up'},
              {'interface': 'et-7/0/10', 'state': 'up'},
              {'interface': 'et-7/0/10.0', 'state': 'up'},
              {'interface': 'et-7/0/11', 'state': 'up'},
              {'interface': 'et-7/0/11.0', 'state': 'up'},
              {'interface': 'et-7/0/12', 'state': 'up'},
              {'interface': 'et-7/0/12.3000', 'state': 'up'},
              {'interface': 'et-7/0/12.32767', 'state': 'up'},
              {'interface': 'et-7/0/13', 'state': 'up'},
              {'interface': 'et-7/0/13.3000', 'state': 'up'},
              {'interface': 'et-7/0/13.32767', 'state': 'up'},
              {'interface': 'et-7/0/14', 'state': 'up'},
              {'interface': 'et-7/0/14.3000', 'state': 'up'},
              {'interface': 'et-7/0/14.32767', 'state': 'up'},
              {'interface': 'et-7/0/15', 'state': 'up'},
              {'interface': 'et-7/0/15.3000', 'state': 'up'},
              {'interface': 'et-7/0/15.32767', 'state': 'up'},
              {'interface': 'et-7/0/16', 'state': 'up'},
              {'interface': 'et-7/0/16.3000', 'state': 'up'},
              {'interface': 'et-7/0/16.32767', 'state': 'up'},
              {'interface': 'et-7/0/17', 'state': 'up'},
              {'interface': 'et-7/0/17.3000', 'state': 'up'},
              {'interface': 'et-7/0/17.32767', 'state': 'up'},
              {'interface': 'et-7/0/19', 'state': 'up'},
              {'interface': 'et-7/0/19.3000', 'state': 'up'},
              {'interface': 'et-7/0/19.3666', 'state': 'up'},
              {'interface': 'et-7/0/19.32767', 'state': 'up'},
              {'interface': 'et-7/0/20', 'state': 'down'},
              {'interface': 'et-7/0/21', 'state': 'up'},
              {'interface': 'et-7/0/22', 'state': 'up'},
              {'interface': 'et-7/0/22.3000', 'state': 'up'},
              {'interface': 'et-7/0/22.3666', 'state': 'up'},
              {'interface': 'et-7/0/22.32767', 'state': 'up'},
              {'interface': 'et-8/0/0', 'state': 'up'},
              {'interface': 'et-8/0/0.3000', 'state': 'up'},
              {'interface': 'et-8/0/0.32767', 'state': 'up'},
              {'interface': 'pfe-8/0/0', 'state': 'up'},
              {'interface': 'pfe-8/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-8/0/0', 'state': 'up'},
              {'interface': 'pfh-8/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-8/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-8/0/0', 'state': 'up'},
              {'interface': 'et-8/0/1', 'state': 'up'},
              {'interface': 'et-8/0/1.3000', 'state': 'up'},
              {'interface': 'et-8/0/1.32767', 'state': 'up'},
              {'interface': 'sxe-8/0/1', 'state': 'up'},
              {'interface': 'et-8/0/2', 'state': 'up'},
              {'interface': 'et-8/0/2.3000', 'state': 'up'},
              {'interface': 'et-8/0/2.32767', 'state': 'up'},
              {'interface': 'sxe-8/0/2', 'state': 'up'},
              {'interface': 'et-8/0/3', 'state': 'up'},
              {'interface': 'et-8/0/3.3000', 'state': 'up'},
              {'interface': 'et-8/0/3.32767', 'state': 'up'},
              {'interface': 'sxe-8/0/3', 'state': 'up'},
              {'interface': 'et-8/0/4', 'state': 'up'},
              {'interface': 'et-8/0/4.3000', 'state': 'up'},
              {'interface': 'et-8/0/4.32767', 'state': 'up'},
              {'interface': 'sxe-8/0/4', 'state': 'up'},
              {'interface': 'et-8/0/5', 'state': 'up'},
              {'interface': 'et-8/0/5.3000', 'state': 'up'},
              {'interface': 'et-8/0/5.32767', 'state': 'up'},
              {'interface': 'sxe-8/0/5', 'state': 'up'},
              {'interface': 'et-8/0/6', 'state': 'up'},
              {'interface': 'et-8/0/6.3000', 'state': 'up'},
              {'interface': 'et-8/0/6.32767', 'state': 'up'},
              {'interface': 'et-8/0/7', 'state': 'up'},
              {'interface': 'et-8/0/7.3000', 'state': 'up'},
              {'interface': 'et-8/0/7.32767', 'state': 'up'},
              {'interface': 'et-8/0/8', 'state': 'up'},
              {'interface': 'et-8/0/8.3000', 'state': 'up'},
              {'interface': 'et-8/0/8.32767', 'state': 'up'},
              {'interface': 'et-8/0/9', 'state': 'up'},
              {'interface': 'et-8/0/9.3000', 'state': 'up'},
              {'interface': 'et-8/0/9.32767', 'state': 'up'},
              {'interface': 'et-8/0/10', 'state': 'up'},
              {'interface': 'et-8/0/10.3000', 'state': 'up'},
              {'interface': 'et-8/0/10.32767', 'state': 'up'},
              {'interface': 'et-8/0/11', 'state': 'up'},
              {'interface': 'et-8/0/11.3000', 'state': 'up'},
              {'interface': 'et-8/0/11.32767', 'state': 'up'},
              {'interface': 'et-8/0/12', 'state': 'up'},
              {'interface': 'et-8/0/12.3000', 'state': 'up'},
              {'interface': 'et-8/0/12.32767', 'state': 'up'},
              {'interface': 'et-8/0/13', 'state': 'down'},
              {'interface': 'et-8/0/13.0', 'state': 'down'},
              {'interface': 'et-8/0/14', 'state': 'up'},
              {'interface': 'et-8/0/14.3000', 'state': 'up'},
              {'interface': 'et-8/0/14.32767', 'state': 'up'},
              {'interface': 'et-8/0/15', 'state': 'down'},
              {'interface': 'et-8/0/15.0', 'state': 'down'},
              {'interface': 'et-8/0/16', 'state': 'up'},
              {'interface': 'et-8/0/16.3000', 'state': 'up'},
              {'interface': 'et-8/0/16.32767', 'state': 'up'},
              {'interface': 'et-8/0/17', 'state': 'down'},
              {'interface': 'et-8/0/17.0', 'state': 'down'},
              {'interface': 'et-8/0/18', 'state': 'down'},
              {'interface': 'et-8/0/18.0', 'state': 'down'},
              {'interface': 'et-8/0/19', 'state': 'up'},
              {'interface': 'et-8/0/19.3000', 'state': 'up'},
              {'interface': 'et-8/0/19.32767', 'state': 'up'},
              {'interface': 'et-8/0/20', 'state': 'up'},
              {'interface': 'et-8/0/20.3000', 'state': 'up'},
              {'interface': 'et-8/0/20.32767', 'state': 'up'},
              {'interface': 'et-8/0/21', 'state': 'up'},
              {'interface': 'et-8/0/21.3000', 'state': 'up'},
              {'interface': 'et-8/0/21.32767', 'state': 'up'},
              {'interface': 'et-8/0/22', 'state': 'down'},
              {'interface': 'et-8/0/22.0', 'state': 'down'},
              {'interface': 'et-8/0/23', 'state': 'up'},
              {'interface': 'et-8/0/23.3000', 'state': 'up'},
              {'interface': 'et-8/0/23.32767', 'state': 'up'},
              {'interface': 'et-8/0/24', 'state': 'down'},
              {'interface': 'et-8/0/24.0', 'state': 'down'},
              {'interface': 'et-8/0/25', 'state': 'down'},
              {'interface': 'et-8/0/25.0', 'state': 'down'},
              {'interface': 'et-8/0/26', 'state': 'down'},
              {'interface': 'et-8/0/26.0', 'state': 'down'},
              {'interface': 'et-8/0/27', 'state': 'up'},
              {'interface': 'et-8/0/27.3000', 'state': 'up'},
              {'interface': 'et-8/0/27.32767', 'state': 'up'},
              {'interface': 'et-8/0/28', 'state': 'up'},
              {'interface': 'et-8/0/28.3000', 'state': 'up'},
              {'interface': 'et-8/0/28.32767', 'state': 'up'},
              {'interface': 'et-8/0/29', 'state': 'up'},
              {'interface': 'et-8/0/29.3000', 'state': 'up'},
              {'interface': 'et-8/0/29.32767', 'state': 'up'},
              {'interface': 'et-9/0/0', 'state': 'up'},
              {'interface': 'et-9/0/0.3000', 'state': 'up'},
              {'interface': 'et-9/0/0.32767', 'state': 'up'},
              {'interface': 'pfe-9/0/0', 'state': 'up'},
              {'interface': 'pfe-9/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-9/0/0', 'state': 'up'},
              {'interface': 'pfh-9/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-9/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-9/0/0', 'state': 'up'},
              {'interface': 'et-9/0/1', 'state': 'up'},
              {'interface': 'et-9/0/1.3000', 'state': 'up'},
              {'interface': 'et-9/0/1.32767', 'state': 'up'},
              {'interface': 'sxe-9/0/1', 'state': 'up'},
              {'interface': 'et-9/0/2', 'state': 'up'},
              {'interface': 'et-9/0/2.3000', 'state': 'up'},
              {'interface': 'et-9/0/2.32767', 'state': 'up'},
              {'interface': 'sxe-9/0/2', 'state': 'up'},
              {'interface': 'et-9/0/3', 'state': 'down'},
              {'interface': 'et-9/0/3.0', 'state': 'down'},
              {'interface': 'sxe-9/0/3', 'state': 'up'},
              {'interface': 'et-9/0/4', 'state': 'up'},
              {'interface': 'et-9/0/4.3000', 'state': 'up'},
              {'interface': 'et-9/0/4.32767', 'state': 'up'},
              {'interface': 'sxe-9/0/4', 'state': 'up'},
              {'interface': 'et-9/0/5', 'state': 'up'},
              {'interface': 'et-9/0/5.3000', 'state': 'up'},
              {'interface': 'et-9/0/5.32767', 'state': 'up'},
              {'interface': 'sxe-9/0/5', 'state': 'up'},
              {'interface': 'et-9/0/6', 'state': 'up'},
              {'interface': 'et-9/0/6.3000', 'state': 'up'},
              {'interface': 'et-9/0/6.32767', 'state': 'up'},
              {'interface': 'et-9/0/7', 'state': 'down'},
              {'interface': 'et-9/0/7.0', 'state': 'down'},
              {'interface': 'et-9/0/8', 'state': 'up'},
              {'interface': 'et-9/0/8.3000', 'state': 'up'},
              {'interface': 'et-9/0/8.32767', 'state': 'up'},
              {'interface': 'et-9/0/9', 'state': 'up'},
              {'interface': 'et-9/0/9.3000', 'state': 'up'},
              {'interface': 'et-9/0/9.32767', 'state': 'up'},
              {'interface': 'et-9/0/10', 'state': 'up'},
              {'interface': 'et-9/0/10.3000', 'state': 'up'},
              {'interface': 'et-9/0/10.32767', 'state': 'up'},
              {'interface': 'et-9/0/11', 'state': 'up'},
              {'interface': 'et-9/0/11.3000', 'state': 'up'},
              {'interface': 'et-9/0/11.32767', 'state': 'up'},
              {'interface': 'et-9/0/12', 'state': 'up'},
              {'interface': 'et-9/0/12.3000', 'state': 'up'},
              {'interface': 'et-9/0/12.32767', 'state': 'up'},
              {'interface': 'et-9/0/13', 'state': 'up'},
              {'interface': 'et-9/0/13.3000', 'state': 'up'},
              {'interface': 'et-9/0/13.32767', 'state': 'up'},
              {'interface': 'et-9/0/14', 'state': 'down'},
              {'interface': 'et-9/0/14.0', 'state': 'down'},
              {'interface': 'et-9/0/15', 'state': 'down'},
              {'interface': 'et-9/0/15.0', 'state': 'down'},
              {'interface': 'et-9/0/16', 'state': 'up'},
              {'interface': 'et-9/0/16.3000', 'state': 'up'},
              {'interface': 'et-9/0/16.32767', 'state': 'up'},
              {'interface': 'et-9/0/17', 'state': 'up'},
              {'interface': 'et-9/0/17.3000', 'state': 'up'},
              {'interface': 'et-9/0/17.32767', 'state': 'up'},
              {'interface': 'et-9/0/18', 'state': 'up'},
              {'interface': 'et-9/0/18.3000', 'state': 'up'},
              {'interface': 'et-9/0/18.32767', 'state': 'up'},
              {'interface': 'et-9/0/19', 'state': 'up'},
              {'interface': 'et-9/0/19.3000', 'state': 'up'},
              {'interface': 'et-9/0/19.32767', 'state': 'up'},
              {'interface': 'et-9/0/20', 'state': 'up'},
              {'interface': 'et-9/0/20.3000', 'state': 'up'},
              {'interface': 'et-9/0/20.32767', 'state': 'up'},
              {'interface': 'et-9/0/21', 'state': 'down'},
              {'interface': 'et-9/0/21.0', 'state': 'down'},
              {'interface': 'et-9/0/22', 'state': 'up'},
              {'interface': 'et-9/0/22.3000', 'state': 'up'},
              {'interface': 'et-9/0/22.32767', 'state': 'up'},
              {'interface': 'et-9/0/23', 'state': 'up'},
              {'interface': 'et-9/0/23.3000', 'state': 'up'},
              {'interface': 'et-9/0/23.32767', 'state': 'up'},
              {'interface': 'et-9/0/24', 'state': 'up'},
              {'interface': 'et-9/0/24.3000', 'state': 'up'},
              {'interface': 'et-9/0/24.32767', 'state': 'up'},
              {'interface': 'et-9/0/25', 'state': 'down'},
              {'interface': 'et-9/0/25.0', 'state': 'down'},
              {'interface': 'et-9/0/26', 'state': 'up'},
              {'interface': 'et-9/0/26.3000', 'state': 'up'},
              {'interface': 'et-9/0/26.32767', 'state': 'up'},
              {'interface': 'et-9/0/27', 'state': 'up'},
              {'interface': 'et-9/0/27.3000', 'state': 'up'},
              {'interface': 'et-9/0/27.32767', 'state': 'up'},
              {'interface': 'et-9/0/28', 'state': 'up'},
              {'interface': 'et-9/0/28.3000', 'state': 'up'},
              {'interface': 'et-9/0/28.32767', 'state': 'up'},
              {'interface': 'et-9/0/29', 'state': 'down'},
              {'interface': 'et-9/0/29.0', 'state': 'down'},
              {'interface': 'et-10/0/0', 'state': 'up'},
              {'interface': 'et-10/0/0.3000', 'state': 'up'},
              {'interface': 'et-10/0/0.32767', 'state': 'up'},
              {'interface': 'pfe-10/0/0', 'state': 'up'},
              {'interface': 'pfe-10/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-10/0/0', 'state': 'up'},
              {'interface': 'pfh-10/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-10/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-10/0/0', 'state': 'up'},
              {'interface': 'et-10/0/1', 'state': 'up'},
              {'interface': 'et-10/0/1.3000', 'state': 'up'},
              {'interface': 'et-10/0/1.32767', 'state': 'up'},
              {'interface': 'sxe-10/0/1', 'state': 'up'},
              {'interface': 'et-10/0/2', 'state': 'up'},
              {'interface': 'et-10/0/2.3000', 'state': 'up'},
              {'interface': 'et-10/0/2.32767', 'state': 'up'},
              {'interface': 'sxe-10/0/2', 'state': 'up'},
              {'interface': 'et-10/0/3', 'state': 'up'},
              {'interface': 'et-10/0/3.3000', 'state': 'up'},
              {'interface': 'et-10/0/3.32767', 'state': 'up'},
              {'interface': 'sxe-10/0/3', 'state': 'up'},
              {'interface': 'et-10/0/4', 'state': 'up'},
              {'interface': 'et-10/0/4.3000', 'state': 'up'},
              {'interface': 'et-10/0/4.32767', 'state': 'up'},
              {'interface': 'sxe-10/0/4', 'state': 'up'},
              {'interface': 'et-10/0/5', 'state': 'up'},
              {'interface': 'et-10/0/5.3000', 'state': 'up'},
              {'interface': 'et-10/0/5.32767', 'state': 'up'},
              {'interface': 'sxe-10/0/5', 'state': 'up'},
              {'interface': 'et-10/0/6', 'state': 'up'},
              {'interface': 'et-10/0/6.3000', 'state': 'up'},
              {'interface': 'et-10/0/6.32767', 'state': 'up'},
              {'interface': 'et-10/0/7', 'state': 'up'},
              {'interface': 'et-10/0/7.3000', 'state': 'up'},
              {'interface': 'et-10/0/7.32767', 'state': 'up'},
              {'interface': 'et-10/0/8', 'state': 'up'},
              {'interface': 'et-10/0/8.3000', 'state': 'up'},
              {'interface': 'et-10/0/8.32767', 'state': 'up'},
              {'interface': 'et-10/0/9', 'state': 'up'},
              {'interface': 'et-10/0/9.3000', 'state': 'up'},
              {'interface': 'et-10/0/9.32767', 'state': 'up'},
              {'interface': 'et-10/0/10', 'state': 'up'},
              {'interface': 'et-10/0/10.3000', 'state': 'up'},
              {'interface': 'et-10/0/10.32767', 'state': 'up'},
              {'interface': 'et-10/0/11', 'state': 'up'},
              {'interface': 'et-10/0/11.3000', 'state': 'up'},
              {'interface': 'et-10/0/11.32767', 'state': 'up'},
              {'interface': 'et-10/0/12', 'state': 'down'},
              {'interface': 'et-10/0/12.0', 'state': 'down'},
              {'interface': 'et-10/0/13', 'state': 'down'},
              {'interface': 'et-10/0/13.0', 'state': 'down'},
              {'interface': 'et-10/0/18', 'state': 'up'},
              {'interface': 'et-10/0/18.3000', 'state': 'up'},
              {'interface': 'et-10/0/18.32767', 'state': 'up'},
              {'interface': 'et-10/0/19', 'state': 'down'},
              {'interface': 'et-10/0/19.0', 'state': 'down'},
              {'interface': 'et-10/0/20', 'state': 'up'},
              {'interface': 'et-10/0/20.3000', 'state': 'up'},
              {'interface': 'et-10/0/20.32767', 'state': 'up'},
              {'interface': 'et-10/0/21', 'state': 'up'},
              {'interface': 'et-10/0/21.3000', 'state': 'up'},
              {'interface': 'et-10/0/21.32767', 'state': 'up'},
              {'interface': 'et-10/0/22', 'state': 'up'},
              {'interface': 'et-10/0/22.3000', 'state': 'up'},
              {'interface': 'et-10/0/22.32767', 'state': 'up'},
              {'interface': 'et-10/0/23', 'state': 'down'},
              {'interface': 'et-10/0/23.0', 'state': 'down'},
              {'interface': 'et-10/0/24', 'state': 'down'},
              {'interface': 'et-10/0/24.0', 'state': 'down'},
              {'interface': 'et-10/0/25', 'state': 'up'},
              {'interface': 'et-10/0/25.3000', 'state': 'up'},
              {'interface': 'et-10/0/25.32767', 'state': 'up'},
              {'interface': 'et-10/0/26', 'state': 'up'},
              {'interface': 'et-10/0/26.3000', 'state': 'up'},
              {'interface': 'et-10/0/26.32767', 'state': 'up'},
              {'interface': 'et-10/0/27', 'state': 'up'},
              {'interface': 'et-10/0/27.3000', 'state': 'up'},
              {'interface': 'et-10/0/27.32767', 'state': 'up'},
              {'interface': 'et-10/0/28', 'state': 'up'},
              {'interface': 'et-10/0/28.3000', 'state': 'up'},
              {'interface': 'et-10/0/28.32767', 'state': 'up'},
              {'interface': 'et-10/0/29', 'state': 'up'},
              {'interface': 'et-10/0/29.3000', 'state': 'up'},
              {'interface': 'et-10/0/29.32767', 'state': 'up'},
              {'interface': 'et-11/0/0', 'state': 'up'},
              {'interface': 'et-11/0/0.3000', 'state': 'up'},
              {'interface': 'et-11/0/0.32767', 'state': 'up'},
              {'interface': 'pfe-11/0/0', 'state': 'up'},
              {'interface': 'pfe-11/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-11/0/0', 'state': 'up'},
              {'interface': 'pfh-11/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-11/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-11/0/0', 'state': 'up'},
              {'interface': 'et-11/0/1', 'state': 'down'},
              {'interface': 'et-11/0/1.0', 'state': 'down'},
              {'interface': 'sxe-11/0/1', 'state': 'up'},
              {'interface': 'et-11/0/2', 'state': 'up'},
              {'interface': 'et-11/0/2.3000', 'state': 'up'},
              {'interface': 'et-11/0/2.32767', 'state': 'up'},
              {'interface': 'sxe-11/0/2', 'state': 'up'},
              {'interface': 'et-11/0/3', 'state': 'down'},
              {'interface': 'et-11/0/3.0', 'state': 'down'},
              {'interface': 'sxe-11/0/3', 'state': 'up'},
              {'interface': 'et-11/0/4', 'state': 'up'},
              {'interface': 'et-11/0/4.3000', 'state': 'up'},
              {'interface': 'et-11/0/4.32767', 'state': 'up'},
              {'interface': 'sxe-11/0/4', 'state': 'up'},
              {'interface': 'et-11/0/5', 'state': 'up'},
              {'interface': 'et-11/0/5.3000', 'state': 'up'},
              {'interface': 'et-11/0/5.32767', 'state': 'up'},
              {'interface': 'sxe-11/0/5', 'state': 'up'},
              {'interface': 'et-11/0/6', 'state': 'up'},
              {'interface': 'et-11/0/6.3000', 'state': 'up'},
              {'interface': 'et-11/0/6.32767', 'state': 'up'},
              {'interface': 'et-11/0/7', 'state': 'up'},
              {'interface': 'et-11/0/7.3000', 'state': 'up'},
              {'interface': 'et-11/0/7.32767', 'state': 'up'},
              {'interface': 'et-11/0/8', 'state': 'up'},
              {'interface': 'et-11/0/8.3000', 'state': 'up'},
              {'interface': 'et-11/0/8.32767', 'state': 'up'},
              {'interface': 'et-11/0/9', 'state': 'up'},
              {'interface': 'et-11/0/9.3000', 'state': 'up'},
              {'interface': 'et-11/0/9.32767', 'state': 'up'},
              {'interface': 'et-11/0/10', 'state': 'up'},
              {'interface': 'et-11/0/10.3000', 'state': 'up'},
              {'interface': 'et-11/0/10.32767', 'state': 'up'},
              {'interface': 'et-11/0/11', 'state': 'up'},
              {'interface': 'et-11/0/11.3000', 'state': 'up'},
              {'interface': 'et-11/0/11.32767', 'state': 'up'},
              {'interface': 'et-11/0/12', 'state': 'down'},
              {'interface': 'et-11/0/12.0', 'state': 'down'},
              {'interface': 'et-11/0/13', 'state': 'down'},
              {'interface': 'et-11/0/13.0', 'state': 'down'},
              {'interface': 'et-11/0/14', 'state': 'up'},
              {'interface': 'et-11/0/14.3000', 'state': 'up'},
              {'interface': 'et-11/0/14.32767', 'state': 'up'},
              {'interface': 'et-11/0/15', 'state': 'up'},
              {'interface': 'et-11/0/15.3000', 'state': 'up'},
              {'interface': 'et-11/0/15.32767', 'state': 'up'},
              {'interface': 'et-11/0/16', 'state': 'up'},
              {'interface': 'et-11/0/16.3000', 'state': 'up'},
              {'interface': 'et-11/0/16.32767', 'state': 'up'},
              {'interface': 'et-11/0/17', 'state': 'down'},
              {'interface': 'et-11/0/17.0', 'state': 'down'},
              {'interface': 'et-11/0/18', 'state': 'up'},
              {'interface': 'et-11/0/18.3000', 'state': 'up'},
              {'interface': 'et-11/0/18.32767', 'state': 'up'},
              {'interface': 'et-11/0/19', 'state': 'up'},
              {'interface': 'et-11/0/19.3000', 'state': 'up'},
              {'interface': 'et-11/0/19.32767', 'state': 'up'},
              {'interface': 'et-11/0/20', 'state': 'up'},
              {'interface': 'et-11/0/20.3000', 'state': 'up'},
              {'interface': 'et-11/0/20.32767', 'state': 'up'},
              {'interface': 'et-11/0/21', 'state': 'up'},
              {'interface': 'et-11/0/21.3000', 'state': 'up'},
              {'interface': 'et-11/0/21.32767', 'state': 'up'},
              {'interface': 'et-11/0/22', 'state': 'up'},
              {'interface': 'et-11/0/22.3000', 'state': 'up'},
              {'interface': 'et-11/0/22.32767', 'state': 'up'},
              {'interface': 'et-11/0/23', 'state': 'up'},
              {'interface': 'et-11/0/23.3000', 'state': 'up'},
              {'interface': 'et-11/0/23.32767', 'state': 'up'},
              {'interface': 'et-11/0/24', 'state': 'up'},
              {'interface': 'et-11/0/24.3000', 'state': 'up'},
              {'interface': 'et-11/0/24.32767', 'state': 'up'},
              {'interface': 'et-11/0/25', 'state': 'down'},
              {'interface': 'et-11/0/25.0', 'state': 'down'},
              {'interface': 'et-11/0/26', 'state': 'up'},
              {'interface': 'et-11/0/26.3000', 'state': 'up'},
              {'interface': 'et-11/0/26.32767', 'state': 'up'},
              {'interface': 'et-11/0/27', 'state': 'up'},
              {'interface': 'et-11/0/27.3000', 'state': 'up'},
              {'interface': 'et-11/0/27.32767', 'state': 'up'},
              {'interface': 'et-11/0/28', 'state': 'up'},
              {'interface': 'et-11/0/28.3000', 'state': 'up'},
              {'interface': 'et-11/0/28.32767', 'state': 'up'},
              {'interface': 'et-11/0/29', 'state': 'down'},
              {'interface': 'et-11/0/29.3000', 'state': 'down'},
              {'interface': 'et-11/0/29.32767', 'state': 'down'},
              {'interface': 'et-12/0/0', 'state': 'up'},
              {'interface': 'et-12/0/0.3000', 'state': 'up'},
              {'interface': 'et-12/0/0.32767', 'state': 'up'},
              {'interface': 'pfe-12/0/0', 'state': 'up'},
              {'interface': 'pfe-12/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-12/0/0', 'state': 'up'},
              {'interface': 'pfh-12/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-12/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-12/0/0', 'state': 'up'},
              {'interface': 'et-12/0/1', 'state': 'up'},
              {'interface': 'et-12/0/1.3000', 'state': 'up'},
              {'interface': 'et-12/0/1.32767', 'state': 'up'},
              {'interface': 'sxe-12/0/1', 'state': 'up'},
              {'interface': 'et-12/0/2', 'state': 'up'},
              {'interface': 'et-12/0/2.3000', 'state': 'up'},
              {'interface': 'et-12/0/2.32767', 'state': 'up'},
              {'interface': 'sxe-12/0/2', 'state': 'up'},
              {'interface': 'et-12/0/3', 'state': 'down'},
              {'interface': 'et-12/0/3.0', 'state': 'down'},
              {'interface': 'sxe-12/0/3', 'state': 'up'},
              {'interface': 'et-12/0/4', 'state': 'down'},
              {'interface': 'et-12/0/4.0', 'state': 'down'},
              {'interface': 'sxe-12/0/4', 'state': 'up'},
              {'interface': 'et-12/0/5', 'state': 'up'},
              {'interface': 'et-12/0/5.3000', 'state': 'up'},
              {'interface': 'et-12/0/5.32767', 'state': 'up'},
              {'interface': 'sxe-12/0/5', 'state': 'up'},
              {'interface': 'et-12/0/6', 'state': 'down'},
              {'interface': 'et-12/0/6.0', 'state': 'down'},
              {'interface': 'et-12/0/7', 'state': 'down'},
              {'interface': 'et-12/0/7.0', 'state': 'down'},
              {'interface': 'et-12/0/8', 'state': 'up'},
              {'interface': 'et-12/0/8.3000', 'state': 'up'},
              {'interface': 'et-12/0/8.32767', 'state': 'up'},
              {'interface': 'et-12/0/9', 'state': 'up'},
              {'interface': 'et-12/0/9.3000', 'state': 'up'},
              {'interface': 'et-12/0/9.32767', 'state': 'up'},
              {'interface': 'et-12/0/10', 'state': 'up'},
              {'interface': 'et-12/0/10.3000', 'state': 'up'},
              {'interface': 'et-12/0/10.32767', 'state': 'up'},
              {'interface': 'et-12/0/11', 'state': 'up'},
              {'interface': 'et-12/0/11.3000', 'state': 'up'},
              {'interface': 'et-12/0/11.32767', 'state': 'up'},
              {'interface': 'et-12/0/13', 'state': 'up'},
              {'interface': 'et-12/0/13.3000', 'state': 'up'},
              {'interface': 'et-12/0/13.3666', 'state': 'up'},
              {'interface': 'et-12/0/13.32767', 'state': 'up'},
              {'interface': 'et-12/0/15', 'state': 'up'},
              {'interface': 'et-12/0/15.3000', 'state': 'up'},
              {'interface': 'et-12/0/15.3666', 'state': 'up'},
              {'interface': 'et-12/0/15.32767', 'state': 'up'},
              {'interface': 'et-12/0/18', 'state': 'up'},
              {'interface': 'et-12/0/18.3000', 'state': 'up'},
              {'interface': 'et-12/0/18.32767', 'state': 'up'},
              {'interface': 'et-12/0/19', 'state': 'up'},
              {'interface': 'et-12/0/19.3000', 'state': 'up'},
              {'interface': 'et-12/0/19.32767', 'state': 'up'},
              {'interface': 'et-12/0/20', 'state': 'up'},
              {'interface': 'et-12/0/20.3000', 'state': 'up'},
              {'interface': 'et-12/0/20.32767', 'state': 'up'},
              {'interface': 'et-12/0/21', 'state': 'up'},
              {'interface': 'et-12/0/21.3000', 'state': 'up'},
              {'interface': 'et-12/0/21.32767', 'state': 'up'},
              {'interface': 'et-12/0/22', 'state': 'up'},
              {'interface': 'et-12/0/22.3000', 'state': 'up'},
              {'interface': 'et-12/0/22.32767', 'state': 'up'},
              {'interface': 'et-12/0/23', 'state': 'up'},
              {'interface': 'et-12/0/23.3000', 'state': 'up'},
              {'interface': 'et-12/0/23.32767', 'state': 'up'},
              {'interface': 'et-12/0/24', 'state': 'up'},
              {'interface': 'et-12/0/24.3000', 'state': 'up'},
              {'interface': 'et-12/0/24.32767', 'state': 'up'},
              {'interface': 'et-12/0/25', 'state': 'up'},
              {'interface': 'et-12/0/25.3000', 'state': 'up'},
              {'interface': 'et-12/0/25.32767', 'state': 'up'},
              {'interface': 'et-12/0/26', 'state': 'up'},
              {'interface': 'et-12/0/26.3000', 'state': 'up'},
              {'interface': 'et-12/0/26.32767', 'state': 'up'},
              {'interface': 'et-12/0/27', 'state': 'up'},
              {'interface': 'et-12/0/27.3000', 'state': 'up'},
              {'interface': 'et-12/0/27.32767', 'state': 'up'},
              {'interface': 'et-12/0/28', 'state': 'up'},
              {'interface': 'et-12/0/28.3000', 'state': 'up'},
              {'interface': 'et-12/0/28.32767', 'state': 'up'},
              {'interface': 'et-12/0/29', 'state': 'up'},
              {'interface': 'et-12/0/29.3000', 'state': 'up'},
              {'interface': 'et-12/0/29.32767', 'state': 'up'},
              {'interface': 'ae1', 'state': 'up'},
              {'interface': 'ae1.0', 'state': 'up'},
              {'interface': 'ae3', 'state': 'up'},
              {'interface': 'ae3.0', 'state': 'up'},
              {'interface': 'ae5', 'state': 'up'},
              {'interface': 'ae5.0', 'state': 'up'},
              {'interface': 'ae7', 'state': 'up'},
              {'interface': 'ae7.0', 'state': 'up'},
              {'interface': 'ae101', 'state': 'up'},
              {'interface': 'ae101.3000', 'state': 'up'},
              {'interface': 'ae101.3666', 'state': 'up'},
              {'interface': 'ae101.32767', 'state': 'up'},
              {'interface': 'ae102', 'state': 'up'},
              {'interface': 'ae102.3000', 'state': 'up'},
              {'interface': 'ae102.3666', 'state': 'up'},
              {'interface': 'ae102.32767', 'state': 'up'},
              {'interface': 'bme0', 'state': 'up'},
              {'interface': 'bme0.0', 'state': 'up'},
              {'interface': 'bme1', 'state': 'up'},
              {'interface': 'bme1.0', 'state': 'up'},
              {'interface': 'bme2', 'state': 'up'},
              {'interface': 'bme2.0', 'state': 'up'},
              {'interface': 'cbp0', 'state': 'up'},
              {'interface': 'dsc', 'state': 'up'},
              {'interface': 'em0', 'state': 'up'},
              {'interface': 'em0.0', 'state': 'up'},
              {'interface': 'em1', 'state': 'down'},
              {'interface': 'em2', 'state': 'up'},
              {'interface': 'em2.32768', 'state': 'up'},
              {'interface': 'esi', 'state': 'up'},
              {'interface': 'gre', 'state': 'up'},
              {'interface': 'ipip', 'state': 'up'},
              {'interface': 'irb', 'state': 'up'},
              {'interface': 'jsrv', 'state': 'up'},
              {'interface': 'jsrv.1', 'state': 'up'},
              {'interface': 'lo0', 'state': 'up'},
              {'interface': 'lo0.0', 'state': 'up'},
              {'interface': 'lo0.16385', 'state': 'up'},
              {'interface': 'lsi', 'state': 'up'},
              {'interface': 'lsi.0', 'state': 'up'},
              {'interface': 'mtun', 'state': 'up'},
              {'interface': 'pimd', 'state': 'up'},
              {'interface': 'pime', 'state': 'up'},
              {'interface': 'pip0', 'state': 'up'},
              {'interface': 'tap', 'state': 'up'},
              {'interface': 'vtep', 'state': 'up'}]
