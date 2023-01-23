function updateData() {
    $.ajax({
        // Настройки
        type: "GET",
        url: "/management/update_my_doors",


        // Функции обработчики
        success: function(response) {
            json = jQuery.parseJSON(response);

            const p_names = $("[id=dr_name]");
            const p_lasts = $("[id=dr_last]");

            for(i=0; i < p_names.length; i++)
            {
                p_name = $(p_names[i]);
                p_last = $(p_lasts[i]);

                p_last.text('Last activity: ' + json['activity_delays'][p_name.text().split(' ')[1]][0]);

                if (json['activity_delays'][p_name.text().split(' ')[1]][1] > 60)
                {
                    p_name.parent().parent().attr('class', 'list-group-item list-group-item-action list-group-item-danger');
                }
                else if (json['activity_delays'][p_name.text().split(' ')[1]][1] > 20)
                {
                    p_name.parent().parent().attr('class', 'list-group-item list-group-item-action list-group-item-warning');
                }
                else
                {
                    p_name.parent().parent().attr('class', 'list-group-item list-group-item-action list-group-item-success');
                }


            }


            //console.log(response)
        },

        error: function(error) {
            console.log(error);
        },

        complete: function() {
            setTimeout(updateData, 1000);
        }
    });
}


setTimeout(updateData, 1000);