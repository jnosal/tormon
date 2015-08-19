Date.prototype.format = function(format) //author: meizz
{
  var o = {
    "M+" : this.getMonth()+1, //month
    "d+" : this.getDate(),    //day
    "h+" : this.getHours(),   //hour
    "m+" : this.getMinutes(), //minute
    "s+" : this.getSeconds(), //second
    "q+" : Math.floor((this.getMonth()+3)/3),  //quarter
    "S" : this.getMilliseconds() //millisecond
  }

  if(/(y+)/.test(format)) format=format.replace(RegExp.$1,
    (this.getFullYear()+"").substr(4 - RegExp.$1.length));
  for(var k in o)if(new RegExp("("+ k +")").test(format))
    format = format.replace(RegExp.$1,
      RegExp.$1.length==1 ? o[k] :
        ("00"+ o[k]).substr((""+ o[k]).length));
  return format;
}


var TormonApp = (function(){
	var module = {};

    module.interval = 4000;

    module.init = function(){
        var self = this;

        self.render_url_status();
        setInterval(self.render_url_status, self.interval);
    };

    module.render_url_status = function(){
        var target = $('#url-status-list tbody'),
            template = _.template($('#url-status-list-tbody-template').html());

        $.ajax({
            method: 'GET',
            url: '/api/urls/',
            contentType: 'application/json',
            dataType: 'json'
        }).done(function(response){
            target.html(template({
                'objects': response.objects
            }));
        });
    };

	return module;
}());


TormonApp.init();