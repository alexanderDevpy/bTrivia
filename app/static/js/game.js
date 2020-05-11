$(function () {
    console.log(document.referrer);
    console.log('ce e aici');
    var protocol = window.location.protocol;




    if( document.referrer == protocol + '//' + document.domain + ':' + location.port + '/lobby' ) {
        $('[data-toggle="popover"]').popover();

        var socket = io.connect(protocol + '//' + document.domain + ':' + location.port + '/game', {transports: ['websocket']});
        $("#exit").on("click", function(){
            $(this).hide();
        });




        var da = $('#hhh').attr("name");
        console.log(da);
        $("#room").text(da);
        socket.on('connect', function () {
            data = {'room': da};
            console.log('consolaaaa', data);
            socket.emit('join', data);
        });

        socket.on('count', function (data) {
            console.log('Count', data);
            socket.emit('update', data);
        });

        socket.on('g', function (data) {
            var users, color;
            users = data.user;
            color = data.color;

            console.log('g', data);
            console.log('sda', $(".info").eq(0).attr("id"));
            for (i = 0; i < 3; i++) {
                if (color[i] == $(".info").eq(0).attr("id")) {
                    $(".info").eq(0).children("p").text(users[i])
                }
                if (color[i] == $(".info").eq(1).attr("id")) {
                    $(".info").eq(1).children("p").text(users[i])
                }
                if (color[i] == $(".info").eq(2).attr("id")) {
                    $(".info").eq(2).children("p").text(users[i])
                }
            }
            console.log(socket.id);
            socket.emit('speed', {'room': data.room});
        });
        var clock;
        var correct;
        socket.on('first', async function (data) {
            $('#overlay').css('display', 'none');
            $('#time').text(' ');
            correct = " ";
            await new Promise(r => setTimeout(r, 2000));
            $('.qe').prop('disabled', false);
            $(".qe").removeClass('btn-success');
            $(".qe").removeClass('btn-danger');
            $('#myModal').modal('show');
            $("#title").text("Round " + data.round);
            $("#question").text(data.questions);
            $("#q1").text(data.answers[0]);
            $("#q2").text(data.answers[1]);
            $("#q3").text(data.answers[2]);
            $("#q4").text(data.answers[3]);
            correct = data.corect;
            console.log(correct)


        });

        socket.on('time', async function (data) {


            clock = setInterval(timing, 1000);

        });


        var cant = 30;

        function timing() {

            if (cant < 0) {
                cant = 30;
                $('.qe').prop('disabled', true);
                clearInterval(clock);
                var sokid = socket.id;
                socket.emit('check', {'ans': "wrong", "room": da, "id": sokid.split("#")[1]});

            } else {
                $("#time").text(cant);
                cant--
            }


        }


        $(".qe").click(function () {
            $('.qe').prop('disabled', true);
            clearInterval(clock);
            $("#overlay").addClass('overlay');
            cant = 30;
            $("#time").text("Waiting for all users to respond");
            var answer = $(this).text();
            var allans = $(this).siblings().text();
            var sokid = socket.id;
            console.log(correct);
            console.log(typeof allans);
            console.log('Id de trimis la sv', sokid.split("#")[1]);
            var data = {"room": da, "ans": answer, "all": allans, "id": sokid.split("#")[1]};
            if (answer == correct) {
                $(this).addClass("btn-success");
                socket.emit('check', {'ans': "correct", "room": da, "id": sokid.split("#")[1]})
            } else {
                $(this).addClass("btn-danger");
                socket.emit('check', {'ans': "wrong", "room": da, "id": sokid.split("#")[1]});
                $(this).siblings().each(function () {
                    let a = $(this).text();
                    if (a == correct) {
                        $(this).addClass("btn-success");
                    }

                });
            }


        });


        socket.on('uptable', async function (data) {
            await new Promise(r => setTimeout(r, 2000));
            $('#myModal').modal('hide');
            var x;
            var l = data;
            $('#overlay').css('display', 'normal');
            for (x in l) {
                console.log("update", l[x][2]);
                console.log(x);

                if (l[x][2] == "correct") {
                    console.log('a ajuns', l[x][0]);
                    var move = $(".player." + l[x][0]).parent();
                    console.log(move);
                    $("." + l[x][0]).appendTo(move.next());
                    if (move.next().attr('id') == $('#par13').attr('id')) {
                        console.log("ai terminat felicitari");
                        socket.emit('win', {'winer': l[x][1], 'room': da})

                    }
                }


            }
            await new Promise(r => setTimeout(r, 4000));
            socket.emit('speed', {'room': da});
        });


        socket.on('finish', async function (data) {

            socket.emit('pleft', {'room': da});
            await new Promise(r => setTimeout(r, 1000));
            $.post("/_finish", {score:data.score}).done(function(response) {
                // success callback
                console.log(response);
                window.location.replace( protocol + '//' + document.domain + ':' + location.port + '/rank');
            }).fail(function() {
                // error callback
                console.log('error')
            })



        });

        socket.on('redirect', async function (data) {

            socket.emit('pleft', {'room': da});
            window.location.replace( protocol + '//' + document.domain + ':' + location.port + '/index');


        });

        socket.on('disconnect', function () {
            socket.emit('leave', {'room': da, "username": socket.id});

        })
    }else {
        await new Promise(r => setTimeout(r, 6000));
        console.log('redirec');
        //window.location.href = protocol + '//' + document.domain + ':' + location.port + '/index';
    }


});
