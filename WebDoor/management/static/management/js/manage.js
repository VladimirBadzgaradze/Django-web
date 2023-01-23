function addTextToConsole(text) {
    pTag = document.createElement("p");
    textNode = document.createTextNode(text);
    pTag.appendChild(textNode);

    consoleObj = document.getElementById("console");
    consoleObj.appendChild(pTag);
}

function clearFirstChild() {
    consoleObj = document.getElementById("console");
    consoleObj.removeChild(consoleObj.firstChild);
}

function updateConsole(outputs) {
    consoleObj = document.getElementById("console");
    if (outputs.length == 0) {
        consoleObj.innerHTML = '';
        return;
    }

    console.log(outputs.length, consoleObj.children.length);
    if (outputs.length <= consoleObj.children.length) {
        return;
    }

    index = consoleObj.children.length;
    for (_ = 0; index < outputs.length; index++) {
        console.log("Adding '" + outputs[index] + "' to console");
        addTextToConsole(outputs[index]);
    }
}


function submitForm() {
    textField = document.getElementById('commandInput');
    if (textField.value.length > 0)
    {
        sendData(textField.value);
        addTextToConsole(">>>> " + textField.value);
        textField.value = "";
    }
}

function sendData(text) { // Функция, вызываемая по кнопке

    $.ajax({
        // Настройки
        type: "POST",
        url: window.location.pathname,
        data: $('form').serialize() + '&text=' + text + '&update=false',

        // Функции обработчики
        success: function(response) {
        },

        error: function(error) {
            console.log(error);
        }
    });
}

function updateData() {
    $.ajax({
        // Настройки
        type: "POST",
        url: window.location.pathname,
        data: $('form').serialize() + "&update=true",


        // Функции обработчики
        success: function(response) {
            json = jQuery.parseJSON(response);
            lst_command = json.last_command;
            answer = json.answer;

            if (($('#console').children().length < 1) && (lst_command.length))
            {
                addTextToConsole(">>>> " + lst_command);
            }

            if (answer.length)
            {
                addTextToConsole(answer);
            }


            //updateConsole(json.outputs);
        },

        error: function(error) {
            console.log(error);
        },

        complete: function() {
            setTimeout(updateData, 500);
        }
    });
}

updateData();