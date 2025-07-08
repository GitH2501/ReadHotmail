


def bypass():
    bypass_js = '''
            var device1={deviceId:"default",kind:"audioinput",label:"",groupId:DanaFP.device1},
            device2={deviceId:"default",kind:"videoinput",label:"",groupId:DanaFP.device2},
            device3={deviceId:"default",kind:"audiooutput",label:"",groupId:DanaFP.device1};
            device1.__proto__=MediaDeviceInfo.prototype,
            device2.__proto__=MediaDeviceInfo.prototype,
            device3.__proto__=MediaDeviceInfo.prototype,
            navigator.mediaDevices.enumerateDevices=function(){
            return new Promise((e,t)=>{e([device1,device2,device3])})
            },
            Object.defineProperty(navigator.mediaDevices.enumerateDevices,"toString",{value:function(){
            return"enumerateDevices() { [native code] }"
            }});
            var settings={enabled:!0,gpuChose:DanaFP.webgl.GPU,parameters:{enabled:!0,list:{
            MAX_TEXTURE_SIZE:13,MAX_VIEWPORT_DIMS:14,RED_BITS:3,GREEN_BITS:3,BLUE_BITS:3,
            ALPHA_BITS:3,STENCIL_BITS:3,MAX_RENDERBUFFER_SIZE:14,MAX_CUBE_MAP_TEXTURE_SIZE:14,
            MAX_VERTEX_ATTRIBS:4,MAX_TEXTURE_IMAGE_UNITS:4,MAX_VERTEX_TEXTURE_IMAGE_UNITS:4,
            MAX_VERTEX_UNIFORM_VECTORS:12}}};
            function safeOverwrite(e,t,a){let n=Object.getOwnPropertyDescriptor(e,t);return n.value=a,n}
            settings.offset=DanaFP.webgl.Random;
            let changeMap={};
            if(settings.parameters.enabled){
            let e={
            3379:Math.pow(2,settings.parameters.list.MAX_TEXTURE_SIZE||14),
            3386:Math.pow(2,settings.parameters.list.MAX_VIEWPORT_DIMS||14),
            3410:Math.pow(2,settings.parameters.list.RED_BITS||3),
            3411:Math.pow(2,settings.parameters.list.GREEN_BITS||3),
            3412:Math.pow(2,settings.parameters.list.BLUE_BITS||3),
            3413:Math.pow(2,settings.parameters.list.ALPHA_BITS||3),
            3414:24,
            3415:Math.pow(2,settings.parameters.list.STENCIL_BITS||3),
            6408:DanaFP.webgl.R6408,
            34024:Math.pow(2,settings.parameters.list.MAX_RENDERBUFFER_SIZE||14),
            30476:Math.pow(2,settings.parameters.list.MAX_CUBE_MAP_TEXTURE_SIZE||14),
            34921:Math.pow(2,settings.parameters.list.MAX_VERTEX_ATTRIBS||4),
            34930:Math.pow(2,settings.parameters.list.MAX_TEXTURE_IMAGE_UNITS||4),
            35660:Math.pow(2,settings.parameters.list.MAX_VERTEX_TEXTURE_IMAGE_UNITS||4),
            35661:DanaFP.webgl.R35661,
            36347:Math.pow(2,settings.parameters.list.MAX_VERTEX_UNIFORM_VECTORS||12),
            36349:Math.pow(2,DanaFP.webgl.R36349),
            7936:settings.ctx_vendor||"WebKit",
            7937:settings.ctx_gpu||"WebKit WebGL",
            37445:settings.debug_vendor||"Intel Inc."
            };
            changeMap=Object.assign(changeMap,e)}
            function updateObject(e,t,a){
            let n=Object.getOwnPropertyDescriptor(e,t)||{configurable:!0};
            n.configurable&&(n.value=a,Object.defineProperty(e,t,n))
            }
            changeMap[37446]=settings.gpuChose;
            ["WebGLRenderingContext","WebGL2RenderingContext"].forEach(function(e){
            if(!window[e])return;
            let t=window[e].prototype.getParameter;
            Object.defineProperty(window[e].prototype,"getParameter",
            safeOverwrite(window[e].prototype,"getParameter",function(e){
            return changeMap[e]?changeMap[e]:t.apply(this,arguments)}));
            let a=window[e].prototype.bufferData;
            Object.defineProperty(window[e].prototype,"bufferData",
            safeOverwrite(window[e].prototype,"bufferData",function(){
            for(let e=0;e<arguments[1].length;e++)arguments[1][e]+=.001*settings.offset;
            return a.apply(this,arguments)}))});
            updateObject(navigator,"buildID",void 0),
            updateObject(navigator,"getUserAgent",void 0),
            updateObject(navigator,"platform",DanaFP.navigator.platform),
            updateObject(navigator,"vendorSub",DanaFP.navigator.vendorSub),
            updateObject(navigator,"productSub",DanaFP.navigator.productSub),
            updateObject(navigator,"vendor",DanaFP.navigator.vendor),
            updateObject(navigator,"hardwareConcurrency",DanaFP.navigator.hardwareConcurrency),
            updateObject(navigator,"appCodeName",DanaFP.navigator.appCodeName),
            updateObject(navigator,"appName",DanaFP.navigator.appName),
            updateObject(navigator,"appVersion",DanaFP.navigator.appVersion),
            updateObject(navigator,"product",DanaFP.navigator.product),
            updateObject(navigator,"language",DanaFP.navigator.language),
            updateObject(navigator,"deviceMemory",DanaFP.navigator.deviceMemory);
            let NetworkInformation=function(){
            this.downlink=DanaFP.navigator.connection.downlink,
            this.downlinkMax=1/0,
            this.effectiveType=DanaFP.navigator.connection.effectiveType,
            this.rtt=DanaFP.navigator.connection.rtt,
            this.saveData=DanaFP.navigator.connection.saveData,
            this.type=DanaFP.navigator.connection.type,
            this.onchange=null,
            this.ontypechange=null,
            this.__proto__=window.NetworkInformation
            },
            fakeNet=new NetworkInformation;
            fakeNet.addEventListener=function(){},
            updateObject(navigator,"connection",fakeNet);
            
            // Thêm listener theo dõi URL ngay trong script khởi tạo
            (function() {
                try {
                    let lastUrl = location.href;
                    
                    // Hàm kiểm tra xem có phải auth redirect URL không
                    function isAuthRedirectUrl(url) {
                        try {
                            const urlObj = new URL(url);
                            return urlObj.hostname === 'localhost' && url.includes('code=');
                        } catch (e) {
                            return false;
                        }
                    }
                    
                    const observer = new MutationObserver(function() {
                        try {
                            if (location.href !== lastUrl) {
                                lastUrl = location.href;
                                console.log('URL_CHANGED:' + lastUrl);
                                
                                if (isAuthRedirectUrl(lastUrl)) {
                                    console.log('AUTH_CODE_FOUND:' + lastUrl);
                                }
                            }
                        } catch (e) {
                            console.error('URL observer error: ' + e.message);
                        }
                    });
                    observer.observe(document, {subtree: true, childList: true});
                    
                    // Cập nhật URL ban đầu
                    console.log('INITIAL_URL:' + location.href);
                } catch (e) {
                    console.error('Failed to setup URL observer: ' + e.message);
                }
            })();
                '''
    


    return bypass_js