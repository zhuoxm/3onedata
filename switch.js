var fs = require('fs');const iconv = require('iconv-lite');
const colors = require('colors');const cors = require('cors');
var readline = require('readline')
var WebSocketClient = require('websocket').client;
var client = new WebSocketClient();
var icmp = require('icmp')

var args = { /* defaults */
    secure: false,
    port: '9090',
    localIPv4: '192.168.200.213',
	publicIPv4_route: '192.168.1.252',
	publicGW_route: '192.168.1.1',
	toPingIp: '192.168.1.250',
	publicIPv4_switch: '192.168.200.213',
	publicGW_switch: '192.168.200.1'
};

var requestOptions = {
    Upgrade: 'websocket',
    Connection: 'Upgrade'
};

var help = '--help(一级菜单):\n1-设置网关ip\n2-启动/停止'
var token = null;
var loopCouts = 0,setSwitchSucess = 0,setSwitchFail = 0,setRouteSucess = 0,setRouteFail = 0,routeVerifyPass = 0,routeVerifyFail = 0;
var mode = null;
var myInterval = null,myTimeout1,myTimeout2,myTimeout3,myTimeout4,myTimeout5,sequence,msg,status,log,result;

//设置DUT网络地址实参
var addr_setKeyArray = new Array('token');
var addr_setInfoArray = new Array('0:设置token','1:下发','(输入-1返回)');
var addr_setCmd = {"cmd":"property_get"};

var login = {"Payload":{"In":{"Password":"MjEyMzJmMjk3YTU3YTVhNzQzODk0YTBlNGE4MDFmYzM=","UserName":"MjEyMzJmMjk3YTU3YTVhNzQzODk0YTBlNGE4MDFmYzM="},"Method":"Login"},"Sequence":1,"Type":"ServiceMethodRequest"};
var setLocalIPv4Cmd = {"Payload":{"In":{"IP":args.localIPv4,"NM":"255.255.255.0","Token":"A3b9jdU4SiUBfnhRC4djP2T8WAp1fImb"},"Method":"SetLocalIPv4Address"},"Sequence":121,"Type":"ServiceMethodRequest"};
var setPublicIPv4_RouteCmd = {"Payload":{"In":{"DHCP": false,"GW": args.publicGW_route,"IP": args.publicIPv4_route,"NM": "255.255.255.0","Route": true,"Token":"A3b9jdU4SiUBfnhRC4djP2T8WAp1fImb"},"Method":"SetPublicIPv4Address"},"Sequence":122,"Type":"ServiceMethodRequest"};
var setPublicIPv4_SwitchCmd = {"Payload":{"In":{"DHCP": false,"GW": args.publicGW_switch,"IP": args.publicIPv4_switch,"NM": "255.255.255.0","Route": false,"Token":"A3b9jdU4SiUBfnhRC4djP2T8WAp1fImb"},"Method":"SetPublicIPv4Address"},"Sequence":122,"Type":"ServiceMethodRequest"};
var routeModeCmd = {"Payload":{"In":{"Enable":true,"Lan":["ge5","ge2","ge3","ge4","ge6","ge7","ge8","gs9","gs10","gs11","gs12"],"Token":"hOxaCI9D9a2iTK9nnhaOwM9ZDPlsjcqE","Wan":["ge1"]},"Method":"SetRouteMode"},"Sequence":2,"Type":"ServiceMethodRequest"};
//var switchMode = {"Payload":{"In":{"DHCP": false,"GW": "192.168.200.1","IP": args.DUT_Ip,"NM": "255.255.255.0","Route": false,"Token":"A3b9jdU4SiUBfnhRC4djP2T8WAp1fImb"},"Method":"SetPublicIPv4Address"},"Sequence":122,"Type":"ServiceMethodRequest"};
var switchModeCmd = {"Payload":{"In":{"Enable":false,"Lan":[],"Token":"FQAGYeTssuWCmDzSUeCthUP4fKYrrmhU","Wan":[]},"Method":"SetRouteMode"},"Sequence":3,"Type":"ServiceMethodRequest"};
var rebootCmd = {"Payload":{"In":{"Token":"FQAGYeTssuWCmDzSUeCthUP4fKYrrmhU"},"Method":"RebootSystem"},"Sequence":4,"Type":"ServiceMethodRequest"};
var res = {"Type":"ServiceMethodResponse","Sequence":46,"Payload":{"Status":0}};

function getNowFormatDate(){
	var date = new Date();var seperator1 = '/';var seperator2 = ':';var month = date.getMonth()+1;var strDate = date.getDate();
	var hour = date.getHours();var minute = date.getMinutes();var second = date.getSeconds();
	if (month >= 1 && month <= 9){month = '0'+month;}
	if (strDate >= 0 && strDate <= 9){strDate = '0'+strDate;}
	if (hour >= 0 && hour <= 9){hour = '0'+hour;}
	if (minute >= 0 && minute <= 9){minute = '0'+minute;}
	if (second >= 0 && second <= 9){second = '0'+second;}
	var currentdate = date.getFullYear()+seperator1+month+seperator1+strDate+' '+hour+seperator2+minute+seperator2+second;
	return currentdate;
}

function setKeyValue(setKey,setValue,isInt,objJson){
	for (var key in objJson){
		var element = objJson[key];
		if (element.length > 0 && typeof element == "object" || typeof element == "object"){
			setKeyValue(setKey,setValue,isInt,element)
		}else if (key == 'messageId'){
		  objJson[key] = messageId;
		}else if (key == 'Token'){
			objJson[key] = token;
		}
	}
	return objJson;
}

function parseJson(jsonObj){
  for (var key in jsonObj){
	var element = jsonObj[key];
	if (element.length > 0 && typeof element == "object" || typeof element == "object"){
		parseJson(element);
	}else if (key.indexOf('timestamp') != -1 || key.indexOf('deviceTime') != -1 || key == 'enterTime' || key == 'exitTime' || key == 'executeTime'){
		console.log(key+":"+element+"(对应北京时间:"+new Date(element*1000).toLocaleString()+")");
	}else{
		//console.log(key+":"+element);
		if (key.indexOf('Token') != -1){
			token = element;
		}	
    }
  }
}

getInput();

function getInput(){ //一级输入，一级菜单选择
	console.log(help);
	rl1 = readline.createInterface({input:process.stdin,output:process.stdout});

	function getInput1(logInfoArray,cmd,keyArray){ //二级输入，二级菜单选择
		var cmd = cmd;
	    var keyArray = keyArray;
	    var logInfoArray = logInfoArray;
	    var isInt;
		rl1.close();
	    rl2 = readline.createInterface({input:process.stdin,output:process.stdout});

	    function getInput2(KEY,isInt){ //三级输入，修改KEY对应的Value
		   rl2.close();
		   rl3 = readline.createInterface({input:process.stdin,output:process.stdout});
		   rl3.on('line',function(line){
			   switch(line){
				   case '-1':rl3.close();getInput1(logInfoArray,cmd,keyArray);break;
			       default:cmd = setKeyValue(KEY,line,isInt,cmd);break;
		        }
		   })
	    }

	    logInfoArray.forEach(function consolelog(item){
			console.log(item);
	    })
		
	    rl2.on('line',function(line){
			if (line == '-1'){
				rl2.close();getInput()
		    }else if (0<= parseInt(line) && parseInt(line)< keyArray.length){
				console.log(logInfoArray[parseInt(line)]+'(输入-1返回二级菜单)');
		    if (logInfoArray[parseInt(line)].indexOf('_isInt') == -1){
				isInt = false;
		    }else{
				isInt = true;
		    }
		    getInput2(keyArray[parseInt(line)],isInt);
		    }else if (parseInt(line) == keyArray.length){
				console.log(logInfoArray[parseInt(line)]);verifyMsgId = cmd['messageId'];
		        var tempCmd = JSON.parse(JSON.stringify(cmd));//console.log('1:',tempCmd);
		        delete tempCmd['isRsp']; //console.log('2:',tempCmd);
		        ws.send(JSON.stringify(tempCmd));
		        console.log('cmd:'+JSON.stringify(tempCmd));
		    }else{
				console.log('输入错误，请重新输入！(输入-1返回一级菜单)');
		    }
	    })
    }

  //一级输入事件监听
	rl1.on('line',function(line){
		switch(line){
			case 'help':console.log(help);break;
            case '1':console.log('请输入网关ip(输入-1返回)');rl1.close();
		      rl2 = readline.createInterface({input:process.stdin,output:process.stdout});
		      rl2.on('line',function(line){
		      	switch(true){
		      		case line == '-1':rl2.close();getInput();break;
		  		    default:args.host = line;break;
		  	    }
		      })
		      break;
			case '2':console.log('请输入，0:启动 1:暂停(输入-1返回)');rl1.close();
		      rl2 = readline.createInterface({input:process.stdin,output:process.stdout});
		      rl2.on('line',function(line){
		      	switch(true){
		      		case line == '-1':rl2.close();getInput();break;
		  		    case line == '0':clearInterval(myInterval),start(),myInterval = setInterval(start,180000);break;
					case line == '1':clearInterval(myInterval);break;
		  		    default:console.log('输入错误，请重新输入(0:启动 1:暂停(输入-1返回))');break;
		  	    }
		      })
		      break;
		  
		default:console.log('输入错误，请重新输入');break;
	}  
})
}

client.on('connectFailed', function(error) {
		console.log('Connect Error: ' + error.toString());
	});

client.on('connect', function(connection) {
	if (0 == loopCouts % 2){
		(async function () {
			result = (await ping()).open;
			if (result == true){
				routeVerifyPass++;
				console.log('['+getNowFormatDate().yellow+']'+'路由转发验证通过'.green+'  (通过:'+routeVerifyPass+' 失败:'+routeVerifyFail+')');
			}else{
				routeVerifyFail++;
				console.log('['+getNowFormatDate().yellow+']'+'result:'+result+' 路由转发验证失败'.red+'  (通过:'+routeVerifyPass+' 失败:'+routeVerifyFail+')');
			}
	    })()
	}
	
	console.log('['+getNowFormatDate().yellow+']'+'WebSocket Client Connected'.green);
	connection.on('error', function(error) {
		console.log('['+getNowFormatDate().yellow+']'+"Connection Error: " + error.toString().red);
	});
	connection.on('close', function() {
		console.log('['+getNowFormatDate().yellow+']'+'Connection Closed'.red);
		connection.drop();
	});

	if (connection.connected) {
		connection.send(Buffer.from(JSON.stringify(login)))
	}
	
	connection.on('message', function(message) {
		//console.log(message['utf8Data']);
		msg = JSON.parse(message['utf8Data']),sequence = msg['Sequence'],status = msg['Payload']['Status'];
		//console.log('this is status:',status);
		parseJson(msg);
		if (status != 0){
			console.log(msg.red);
		}
		
		if (sequence == 1 && status == 0){
			routeModeCmd = setKeyValue('token',token,false,routeModeCmd);
			switchModeCmd = setKeyValue('token',token,false,switchModeCmd);
			rebootCmd = setKeyValue('token',token,false,rebootCmd);
			setLocalIPv4Cmd = setKeyValue('token',token,false,setLocalIPv4Cmd);
			setPublicIPv4_RouteCmd = setKeyValue('token',token,false,setPublicIPv4_RouteCmd);
			setPublicIPv4_SwitchCmd = setKeyValue('token',token,false,setPublicIPv4_SwitchCmd);
			
			if (token != null && sequence == 1){
				//console.log(loopCouts)
				if (0 == loopCouts % 2){
					//console.log('set switch mode');
					mode = 'switchMode';
					//myTimeout1 = setTimeout(setPublicIPv4_switch,'200');
					myTimeout2 = setTimeout(setSwitch,'500');
				}else if (1 == loopCouts % 2){
					//console.log('set router mode');
					mode = 'routeMode';
					//myTimeout1 = setTimeout(setLocalIPv4,'200');
					//myTimeout2 = setTimeout(setPublicIPv4_route,'300');
					myTimeout3 = setTimeout(setRoute,'500');
					myTimeout4 = setTimeout(reboot,'1000');
				}
			}
		}
		
		//console.log('this is mode:',mode,'this is status:',status);
		if (mode == 'routeMode' && sequence == 2 && status == 0){
			setRouteSucess++;
			log = 'The '+loopCouts+' times, set router mode success! gateway will reboot....';
			console.log('['+getNowFormatDate().yellow+']'+log.green+' (设置成功统计- router:'+setRouteSucess+' switch:'+setSwitchSucess+' 设置失败统计- router:'+setRouteFail+' switch:'+setSwitchFail+')');
			myTimeout4 = setTimeout(reboot,'1000')
		}else if (mode == 'routeMode' && sequence == 2 && status != 0){
			setRouteFail++;
			log = 'The '+loopCouts+' times, set router mode failed!'
			console.log('['+getNowFormatDate().yellow+']'+log.red+' (设置成功统计- router:'+setRouteSucess+' switch:'+setSwitchSucess+' 设置失败统计- router:'+setRouteFail+' switch:'+setSwitchFail+')');
		}else if (mode == 'switchMode' && sequence == 3 && status == 0){
			setSwitchSucess++;
			log = 'The '+loopCouts+' times, set switch mode success! gateway will reboot....'
			console.log('['+getNowFormatDate().yellow+']'+log.green+' (设置成功统计- router:'+setRouteSucess+' switch:'+setSwitchSucess+' 设置失败统计- router:'+setRouteFail+' switch:'+setSwitchFail+')');
			myTimeout4 = setTimeout(reboot,'1000')
		}else if (mode == 'switchMode' && sequence == 3 && status != 0){
			setSwitchFail++;
			log = 'The '+loopCouts+' times, set switch mode failed!'
			console.log('['+getNowFormatDate().yellow+']'+log.red+' (设置成功统计- router:'+setRouteSucess+' switch:'+setSwitchSucess+' 设置失败统计- router:'+setRouteFail+' switch:'+setSwitchFail+')');
		}
		
		myTimeout5 = setTimeout(closeCon,'3500')
		
	});

	function setLocalIPv4(){
		connection.send(Buffer.from(JSON.stringify(setLocalIPv4Cmd)));
	}
	
	function setPublicIPv4_route(){
		connection.send(Buffer.from(JSON.stringify(setPublicIPv4_RouteCmd)));
	}
	
	function setPublicIPv4_switch(){
		connection.send(Buffer.from(JSON.stringify(setPublicIPv4_SwitchCmd)));
	}
	
	function setRoute(){
		connection.send(Buffer.from(JSON.stringify(routeModeCmd)));
	}
	
	function setSwitch(){
		connection.send(Buffer.from(JSON.stringify(switchModeCmd)));
	}
	
	function reboot(){
		connection.send(Buffer.from(JSON.stringify(rebootCmd)));
	}
	
	function closeCon(){
		connection.close();
	}
	
	function ping(){
		return icmp.ping(args.toPingIp,5000)
	}
	
});	

function start(){
	loopCouts++;
	client.connect('ws://'+args.publicIPv4_switch+':'+args.port+'/config', requestOptions,'echo-protocol');	
}	