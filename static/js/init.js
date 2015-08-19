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