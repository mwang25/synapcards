// Copyright 2016, Google, Inc.
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

$(function(){
  // This is the host for the backend.
  // TODO: When running Firenotes locally, set to http://localhost:8081. Before
  // deploying the application to a live production environment, change to
  // https://backend-dot-<PROJECT_ID>.appspot.com as specified in the
  // backend's app.yaml file.
  // var backendHostUrl = 'https://backend-dot-fireproto-5c009.appspot.com';
  var backendHostUrl = 'https://synapcards.com';

  // Initialize Firebase
  var config = {
    apiKey: "AIzaSyCOrg4vnNpWniyNPB4_Gy2n0mv5t95DJJI",
    authDomain: "synapcards-178123.firebaseapp.com",
    databaseURL: "https://synapcards-178123.firebaseio.com",
    projectId: "synapcards-178123",
    storageBucket: "synapcards-178123.appspot.com",
    messagingSenderId: "266358714814"
  };

  // This is passed into the backend to authenticate the user.
  var userIdToken = null;
  // Signed in user data stored across functions.
  var userData = null;
  var accountDeleted = false;

  // Firebase log-in
  function configureFirebaseLogin() {

    firebase.initializeApp(config);

    // [START onAuthStateChanged]
    firebase.auth().onAuthStateChanged(function(user) {
      if (user) {
        user.getToken().then(function(idToken) {
          userIdToken = idToken;
          $('#signed-in-top').show();
          $('#signed-out-top').hide();
          $('#static-info-section').show();
          $('#follow-button-section').hide();
          $('#unfollow-button-section').hide();
          $('#dynamic-info-section').hide();
          $('#form-section').hide();
          $('#edit-buttons-section').hide();
          $('#account-deleted-section').hide();
          $('#main-section').show();
          $('#add-new-card-section').hide();
          $.ajax(backendHostUrl + '/signinajax', {
            headers: {
              'Authorization': 'Bearer ' + userIdToken
            }
          }).then(function(data){
            userData = data;
            $('#signed-in-user-id-top').text(userData.signed_in_user_id);
            link = backendHostUrl + '/user/' + userData.signed_in_user_id;
            $('#self-profile-link-top').attr('href', link);
            // Extract user_id from last element, which may contain ?follow=
            last = window.location.href.split("/").pop()
            page_user_id = last.match(/[\w\d_\.]+/)[0]
            console.log("user_id = " + page_user_id)
            if (page_user_id === data.signed_in_user_id) {
              $('#static-info-section').hide();
              $('#dynamic-info-section').show();
              $('#edit-buttons-section').show();
              link = backendHostUrl + '/card/' + data.signed_in_user_id + ':0';
              $('#add-new-card-link').attr('href', link);
              $('#add-new-card-section').show();
            } else {
              // signed in, but looking at another user's profile page
              if (data.following.includes(page_user_id)) {
                $('#unfollow-button-section').show();
              } else {
                $('#follow-button-section').show();
              }
            }
          });
        });
      } else {
        // Signed out state.
        $('#signed-in-top').hide();
        $('#signed-out-top').show();
        if (accountDeleted) {
          $('#account-deleted-section').show();
          $('#main-section').hide();
          $('#static-info-section').hide();
          $('#follow-button-section').hide();
          $('#unfollow-button-section').hide();
          $('#dynamic-info-section').hide();
        } else {
          $('#account-deleted-section').hide();
          $('#main-section').show();
          $('#static-info-section').show();
          $('#follow-button-section').hide();
          $('#unfollow-button-section').hide();
          $('#dynamic-info-section').hide();
        }
        $('#form-section').hide();
        $('#edit-buttons-section').hide();
        $('#add-new-card-section').hide();
      }
    });
  }

  var signOutBtn =$('#sign-out');
  signOutBtn.click(function(event) {
    event.preventDefault();

    firebase.auth().signOut().then(function() {
      console.log("Sign out successful");
      userIdToken = null;
      userData = null;
    }, function(error) {
      console.log(error);
    });
  });

  var deleteAccountBtn =$('#delete-account-button');
  deleteAccountBtn.click(function(event) {
    event.preventDefault();
    if (window.confirm('Delete your account and all your cards?') == true){
      $.ajax(backendHostUrl + '/userajax', {
        headers: {
          'Authorization': 'Bearer ' + userIdToken
        },
        method: 'POST',
        data: JSON.stringify({
          'action': 'delete',
        }),
        contentType : 'application/json'
      }).then(function(data){
        if ('error_message' in data) {
          console.log("delete error detected: " + data.error_message)
          window.alert(data.error_message);
        } else {
          console.log("delete success");
          accountDeleted = true;
          userIdToken = null;
          userData = null;
          firebase.auth().signOut()
        }
      });
    }
  });

  var editBtn =$('#edit-button');
  editBtn.click(function(event) {
    event.preventDefault();
    $('#static-info-section').hide();
    $('#dynamic-info-section').hide();
    $('#form-section').show();
    $('#edit-buttons-section').hide();
    if (userData.total_cards > 0) {
      console.log("plain text userid " + userData.total_cards);
      $('#form-userid-rw').hide();
      $('#form-userid-ro').show();
    } else {
      console.log("text input userid " + userData.total_cards);
      $('#form-userid-rw').show();
      $('#form-userid-ro').hide();
    }
    // Populate form fields.
    $('#form-userid-container').text(userData.user_id);
    document.getElementById("userid-textinput").defaultValue = userData.user_id;
    document.getElementById("email-textinput").defaultValue = userData.email;
    document.getElementById("profile-textarea").defaultValue = userData.profile;
    console.log("update freq from backend: " + userData.update_frequency);
    var dropdown = document.getElementById("update-frequency-dropdown");
    for (var i = 0; i < dropdown.options.length; i++) {
       if (dropdown.options[i].value == userData.update_frequency) {
           dropdown.options[i].selected = true;
       }
    }
    console.log("timezone from backend: " + userData.timezone);
    var dropdown = document.getElementById("timezone-dropdown");
    for (var i = 0; i < dropdown.options.length; i++) {
       if (dropdown.options[i].value == userData.timezone) {
           dropdown.options[i].selected = true;
       }
    }
  });

  var cancelBtn =$('#cancel-button');
  cancelBtn.click(function(event) {
    event.preventDefault();
    $('#static-info-section').hide();
    $('#dynamic-info-section').show();
    $('#form-section').hide();
    document.getElementById("userid-textinput").value = userData.user_id;
    document.getElementById("email-textinput").value = userData.email;
    document.getElementById("profile-textarea").value = userData.profile;
    var dropdown = document.getElementById("timezone-dropdown");
    for (var i = 0; i < dropdown.options.length; i++) {
       if (dropdown.options[i].value == userData.timezone) {
           dropdown.options[i].selected = true;
       }
    }
    $('#error-user-id-container').empty();
    $('#edit-buttons-section').show();
  });

  var saveBtn = $('#save-button');
  saveBtn.click(function(event) {
    console.log("Save button hit");
    event.preventDefault();

    var userid = $('#userid-textinput').val();
    var email = $('#email-textinput').val();
    var update_frequency = $('#update-frequency-dropdown').val();
    var timezone = $('#timezone-dropdown').val();
    var profile = $('#profile-textarea').val();

    $.ajax(backendHostUrl + '/userajax', {
      headers: {
        'Authorization': 'Bearer ' + userIdToken
      },
      method: 'POST',
      data: JSON.stringify({
        'action': 'edit',
        'user_id': userid,
        'email': email,
        'profile': profile,
        'update_frequency': update_frequency,
        'timezone': timezone,
      }),
      contentType : 'application/json'
    }).then(function(data){
      // Hide form container and display updated user info data.
      if ('error_message' in data) {
        console.log("error detected: " + data.error_message)
        $('#error-user-id-container').text(data.error_message);
      } else {
        console.log("post success, reload page");
        url = backendHostUrl + '/user/' + userid;
        window.location.href=url;
      }
    });
  });

  function followAjax(action, user_id) {
    event.preventDefault();
    $.ajax(backendHostUrl + '/userajax', {
      headers: {
        'Authorization': 'Bearer ' + userIdToken
      },
      method: 'POST',
      data: JSON.stringify({
        'action': action,
        'user_id': user_id,
      }),
      contentType : 'application/json'
    }).then(function(data){
      if ('error_message' in data) {
        console.log("error detected: " + data.error_message)
      } else {
        console.log("post success, reload page");
        url = backendHostUrl + '/user/' + user_id;
        window.location.href=url;
      }
    })
  }

  var followOtherBtn = $('#follow-other-button');
  followOtherBtn.click(function(event) {
    console.log("Follow other button hit: " + page_user_id);
    followAjax('follow', page_user_id)
  });

  var unfollowOtherBtn = $('#unfollow-other-button');
  unfollowOtherBtn.click(function(event) {
    console.log("Unfollow other button hit: " + page_user_id);
    followAjax('unfollow', page_user_id)
  });

  var followSelfBtn = $('#follow-self-button');
  followSelfBtn.click(function(event) {
    console.log("Follow self button hit: " + page_user_id);
    followAjax('follow', page_user_id)
  });

  var unfollowSelfBtn = $('#unfollow-self-button');
  unfollowSelfBtn.click(function(event) {
    console.log("Unfollow self button hit: " + page_user_id);
    followAjax('unfollow', page_user_id)
  });

  configureFirebaseLogin();
});
