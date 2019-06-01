(function(){
  var messageResponses = '';
  var main = {
    socket: null,
    init: function() {
      this.cacheDOM();
      this.subscribe();
      this.bindEvents();

    },
    cacheDOM: function() {
      this.$submit_task_btn = $('#submit_task');

    },
    bindEvents: function() {
      this.$submit_task_btn.on('click', this.submitJob.bind(this));
    },

    submitJob: function() {

      var r = confirm("Are you Sure you want to submit?");
      if (r == true) {
        stopTimer();
        this.socket.emit('submit_active', {
          worker: this.gup("workerId"),
          time_waited: result,
          reward: reward,
          aid: this.gup("assignmentId"),
          hit_id: this.gup("hitId")
        });
        this.socket.disconnect();
        // submit to AMT server
        var string = "SUBMIT_WORK_ACTIVE";
        $('input[name="user-input"]').val(string);
        $("#endForm").submit();
      }
    },

    gup:function(name) {
        name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
        var regexS = "[\\?&]"+name+"=([^&#]*)";
        var regex = new RegExp(regexS);
        var results = regex.exec(window.location.href);
        if(results == null)
         return "";
        else
         return unescape(results[1]);
    },

    //you can write events for socketIO
    subscribe:function() {
      var namespace = '/chat';
      this.socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
      console.log(location.protocol + '//' + document.domain + ':' + location.port + namespace);

      //start timer as soon as they reach this page
      startTimer();
    },

   updateScore: function(data){
     //check whether this worker is the one who should get notification for score update
     if(data.workerId === this.gup("workerId")) {
       $('#total_msgs').text(data.total_msgs);
       $("#selected_msgs").text(data.selected_msgs);
       $("#total_bonus").text(data.bonus);
     }
   },

   stopJob: function(data) {

     stopTimer();

     // alert("The requester wants to finish this job now." +
     // "You will be paid (fix pay as well as bonuses) based on your contribution in waiting and active state.");

     this.socket.emit('submit_active', {
       worker: this.gup("workerId"),
       time_waited: result,
       reward: reward,
       aid: this.gup("assignmentId"),
       hit_id: this.gup("hitId")
     });
     this.socket.disconnect();
     // submit to AMT server
     var string = "SUBMIT_WORK_ACTIVE";
     $('input[name="user-input"]').val(string);
     $("#endForm").submit();

   },

  };

  main.init();



})();
