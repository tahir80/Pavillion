// var voting;

(function() {
  var waiting = {
    socket: null,
    workerId: '',
    isJobFull: false,

    init: function() {
      this.cacheDOM();
      this.subscribe();
      this.bindEvents();
      this.isTaskAccepted();
      //this.receive_message();
    },
    cacheDOM: function() {

      this.$submit_task_btn = $('#submit_task');
      this.$timer = $('#timer');
      this.$reward = $('#reward');
      this.$worker_count = $('#worker_count');
      this.$end_dialog_message = $("#end-dialog-message");
    },



    gup: function(name) {
      name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
      var regexS = "[\\?&]" + name + "=([^&#]*)";
      var regex = new RegExp(regexS);
      var results = regex.exec(window.location.href);
      if (results == null)
        return "";
      else
        return unescape(results[1]);
    },

    bindEvents: function() {
      this.$submit_task_btn.on('click', this.submitJob.bind(this));
      $(window).on('beforeunload', this.handle_io.bind(this));
      // $(window).on('beforeunload', this.preventReload.bind(this));
      // $("#hello").on('click', this.hello.bind(this));
    },

    handle_io: function() {
      this.socket.close();
    },

    submitJob: function() {

      var r = confirm("Are you Sure you want to submit?");
      if (r == true) {
        stopTimer();
        this.socket.emit('submit_waiting', {
          worker: this.gup("workerId"),
          time_waited: result,
          reward: reward,
          aid: this.gup("assignmentId"),
          hit_id: this.gup("hitId")
        });
        this.socket.disconnect();
        // submit to AMT server
        var string = "SUBMIT_WORK_WAITING";
        $('input[name="user-input"]').val(string);
        $("#endForm").submit();
      }

    },

    isTaskAccepted: function() {
      //when the task is not accepted yet
      if (this.gup("assignmentId") == "ASSIGNMENT_ID_NOT_AVAILABLE") {
        this.$start_task_btn.attr("DISABLED", "disabled");
        this.$submit_task_btn.attr("DISABLED", "disabled");
      } else {
        //when the task is accepted. Do not let them to enter into main task
        this.$start_task_btn.attr("DISABLED", "disabled");

        this.socket.emit('connected', {
          workerId: this.gup("workerId"),
          aid: this.gup("assignmentId"),
          hit_id: this.gup("hitId")
        });

        startTimer();
      }
    },
    subscribe: function() {
      // console.log("https://pepperanywhere.herokuapp.com/main_task/?assignmentId="+this.gup("assignmentId")+"&" + "hitId=" +this.gup("hitId") +
      //                                                                                              "&" + "workerId=" + this.gup("workerId"));
      var namespace = '/chat';
      this.socket = io.connect(location.protocol + '//' + document.domain + location.port + namespace);
      // console.log(location.protocol + '//' + document.domain + ':' + location.port + namespace);
      this.socket.on('start_your_task', function(e) {
        for (var key in e.message) {
          if (e.message[key] === this.gup("workerId")) {
            stopTimer();
            //this will store waiting bonus to the DB before pushing worker to main task
            this.socket.emit('IAmReady', {
              worker: this.gup("workerId"),
              aid: this.gup("assignmentId"),
              hit_id: this.gup("hitId"),
              time_waited: result,
              reward: reward
            });

            this.socket.disconnect();

            var assignmentId = this.gup("assignmentId");
            var hitId = this.gup("hitId");
            var workerId = this.gup("workerId");
            var turkSubmitTo = this.gup("turkSubmitTo");

            window.location.replace("YOUR_DOMAIN" +"?hitId="+hitId+"&assignmentId="+assignmentId+"&workerId="+workerId+"&turkSubmitTo="+turkSubmitTo+"&time_waited=" + result + "&reward=" + reward);
            break;
          }
        }
      }.bind(this));
      // Job is already full
      this.socket.on('job_is_full', function(e) {
        if (e.id === this.gup("workerId")) {
          this.isJobFull = true;
          stopTimer();
          this.$submit_task_btn.attr("DISABLED", "disabled");
          alert(e.message);
        }
      }.bind(this));

      //to update total number of workers on web page
      this.socket.on('update_worker_count', function(e) {
        console.log(e.count + " / " + e.max_count + "Workers Hired!");
        this.$worker_count.text(e.count + " / " + e.max_count + "Workers Hired!");
      }.bind(this));

      //update chat on each new message
      this.socket.on('stop', function(e) {
        if (this.gup("assignmentId") == "ASSIGNMENT_ID_NOT_AVAILABLE" || this.isJobFull == true) {} //if job was filled or s/he did not accept job yet, don't send message
        else {
        stopTimer();
        // alert("The requester wants to finish this job now." +
        //   "You will be paid (fix pay as well as bonuses) based on your contribution in waiting and active state.");

        this.socket.emit('submit_waiting', {
          worker: this.gup("workerId"),
          time_waited: result,
          reward: reward,
          aid: this.gup("assignmentId"),
          hit_id: this.gup("hitId")

        });
        this.socket.disconnect();
        // submit to AMT server
        var string = "SUBMIT_WORK_WAITING";
        $('input[name="user-input"]').val(string);
        $("#endForm").submit();
      }
      }.bind(this));

    } //end of subscribe
  };

  waiting.init();

})();
