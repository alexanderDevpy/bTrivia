$(function () {
    var protocol = window.location.protocol;
    var socket = io.connect(protocol + '//' + document.domain + ':' + location.port + '/lobby', {transports: ['websocket']});

    var cont = 1;

    socket.on('connect', function (sessionID) {
        console.log(socket.id);
        socket.send(socket.id);
        cont += 1;
    });
    var h1 = '';
    socket.on('user', function (data) {
        const sessionID = socket.id;
        console.log(sessionID, data);

        $('#hhh').text(data.user);
        cont += 1;
    });


    var tare = " ";
    socket.on('start', function (data) {
        gameroom = data.url;
        socket.disconnect();
        window.location.replace( protocol + '//' + document.domain + ':' + location.port + '/game' + '/' + gameroom);

    });

    function now(data) {

        console.log('tansssadsdasddn functie', tare);

    };
    setInterval(now, 3000);
});