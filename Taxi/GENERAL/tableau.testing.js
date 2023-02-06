/*!
* TabUI v. 2.05
* Date: 2022-04-04
* Description: https://wiki.yandex-team.ru/taxi/analytics/tools/tableau/server/custom-js/
* Ticket: https://st.yandex-team.ru/DMPDEV-5305
* 
* Dependencies:
*     Script utilizes imported by default libriaries:
*     — underscore-min.js     http://underscorejs.org/
*    — js.cookie.js          https://github.com/js-cookie/js-cookie
* 
*     It also uses librarires imported manualy:
*     — Tippy JS            — the complete tooltip, popover, dropdown, and menu solution for the web, (https://atomiks.github.io/tippyjs/)
*     — Jquery Toast Plugin — highly customizable jquery plugin to show toast messages (https://kamranahmed.info/toast)
*     — Staff-card          — pop-up card with Staff info (https://github.yandex-team.ru/tools/staff-card)
*
*/

(function ($) {
  $.fn.drags = function (opt) {
    opt = $.extend({ handle: "", cursor: "move" }, opt);

    if (opt.handle === "") {
      var $el = this;
    } else {
      var $el = this.find(opt.handle);
    }

    return $el
      .css("cursor", opt.cursor)
      .on("mousedown", function (e) {
        if (opt.handle === "") {
          var $drag = $(this).addClass("draggable");
        } else {
          var $drag = $(this)
            .addClass("active-handle")
            .parent()
            .addClass("draggable");
        }
        var z_idx = $drag.css("z-index"),
          drg_h = $drag.outerHeight(),
          drg_w = $drag.outerWidth(),
          pos_y = $drag.offset().top + drg_h - e.pageY,
          pos_x = $drag.offset().left + drg_w - e.pageX;
        $drag
          .css("z-index", 1000)
          .parents()
          .on("mousemove", function (e) {
            $(".draggable")
              .offset({
                top: e.pageY + pos_y - drg_h,
                left: e.pageX + pos_x - drg_w,
              })
              .on("mouseup", function () {
                $(this).removeClass("draggable").css("z-index", z_idx);
              });
          });
        e.preventDefault(); // disable selection
      })
      .on("mouseup", function () {
        if (opt.handle === "") {
          $(this).removeClass("draggable");
        } else {
          $(this)
            .removeClass("active-handle")
            .parent()
            .removeClass("draggable");
        }
      });
  };
})(jQuery);


(function(window, document, undefined) {

  var TablUILocator = function (navUrls = {oldUrl: window.location, newUrl: window.location}){
    /* Function parses hashes and return current directory
    Usage within hashchange event: 
    currentDirectory = TablLocator({oldUrl: event.oldURL, newUrl: event.newURL}).currentDir;
    */
    var getDir = (hash) => {
      var dirs = {
        'home'            : /home/,
        'explore'         : /explore/,
        'user'            : /user\//,
        'favorites'       : /favorites/,
        'project'         : /projects\/.*$/,
        'workbook'        : /workbooks\/(?<workbookID>\d+)\/(?<subDirectory>.*)?$/,
        'view'            : /views\/.*\/.*/,
        'view-redirect'   : /redirect_to_view\/\d+$/,
        'datasource'      : /datasources\/(?<datasourceID>\d+)\/(?<subDirectory>.*)?$/,
        'recents'         : /recents/,
        'recommendations' : /recommendations/,
        'shared'          : /sharedWithMe/,
        'collections-my'  : /collections\/myCollections/,
        'collections-all' : /collections\/allCollections/
      }
      
      return Object.keys(dirs).filter(key => dirs[key].test(hash))[0]
      
    }
    var getLocation = (urls) => {
      return {
        oldHash : new URL(urls.oldUrl).hash.substr(2).split('?')[0],
        newHash : new URL(urls.newUrl).hash.substr(2).split('?')[0]
      }
    }
    var getHashParts = (urls) => {
      //TODO: automaticaly create hashparts objects from regex groups
      let hash = new URL(urls.newUrl).hash.substr(2).split('?')[0]
      let dir = getDir(getLocation(urls).newHash)
      if (dir == 'workbook'){
        return {
          id: hash.match(/workbooks\/(?<workbookID>\d+)\/(?<subDirectory>.*)?$/).groups.workbookID,
          name: dir,
          subDirectory: hash.match(/workbooks\/(?<workbookID>\d+)\/(?<subDirectory>.*)?$/).groups.subDirectory
        }
      }
      if (dir == 'datasource'){
        return {
          id: hash.match(/datasources\/(?<datasourceID>\d+)\/(?<subDirectory>.*)?$/).groups.datasourceID,
          name: dir,
          subDirectory: hash.match( /datasources\/(?<datasourceID>\d+)\/(?<subDirectory>.*)?$/).groups.subDirectory
        }
      }
      if (dir == 'project'){
        return {
          id: hash.match(/projects\/(?<projectID>\d+)?$/).groups.projectID,
          name: dir,
          subDirectory: ''
        }
      }
      if (dir == 'view'){
        return {
          id: hash.match(/views\/(?<workbookID>[^\/]*)\/(?<subDirectory>[^\/\?\n]*)/).groups.workbookID,
          name: dir,
          subDirectory: hash.match(/views\/(?<workbookID>[^\/]*)\/(?<subDirectory>[^\/\?\n]*)/).groups.subDirectory
        }
      }
      if (dir == 'user'){
        return {
          id: hash.match(/user\/(?<domain>[^\/]*)\/(?<id>[^\/]*)\/(?<subDirectory>[^\/]*)/).groups.id,
          name: dir,
          subDirectory: hash.match(/user\/(?<domain>[^\/]*)\/(?<id>[^\/]*)\/(?<subDirectory>[^\/]*)/).groups.subDirectory
        }
      }
    }
    return {
        currentDir : getDir(getLocation(navUrls).newHash),
        hashParts  : getHashParts(navUrls)
    }
  };

  var TabUI = {
          context : {
            user : {
              login : Cookies.get("yandex_login"),
              token : Cookies.get("XSRF-TOKEN")
            },
            toasts : {
              shown   : localStorage.getItem("TabUIToastShown") ? JSON.parse(localStorage.getItem("TabUIToastShown")) : [], 
              hidden  : localStorage.getItem("TabUIToastHidden") ? JSON.parse(localStorage.getItem("TabUIToastHidden")) : []
            },
            currentUserMeta : localStorage.getItem("currentUserMeta") ? JSON.parse(localStorage.getItem("currentUserMeta")) : {},
            certifiedWorkbooks : localStorage.getItem("certifiedWorkbooks")? JSON.parse(localStorage.getItem("certifiedWorkbooks")) : [],
            currentDirectory : {
              name: TablUILocator().currentDir
            }
          },
          icons : {
            idm: `<svg id="idm_icon" width="24" height="24" viewBox="0 0 96 96" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" overflow="hidden"><g id="Icons"><path d="M43.5 38.011C37.9772 27.8086 25.2294 24.0151 15.027 29.538 4.82463 35.0608 1.03114 47.8086 6.55398 58.011 12.0768 68.2134 24.8246 72.0069 35.027 66.484 38.6141 64.5422 41.5582 61.5981 43.5 58.011L50 58.011 54 54.011 58 58.011 64.5 51.511 71 58.011 77.5 51.511 84 58.011 92 48.011 84 38.011ZM83.836 55.021 78.918 50.1 77.5 48.686 76.089 50.1 71 55.188 65.918 50.1 64.5 48.686 63.089 50.1 58 55.188 55.417 52.6 54 51.187 52.588 52.6 49.174 56.015 42.315 56.015 41.746 57.058C36.7503 66.2897 25.2167 69.7237 15.985 64.728 6.75333 59.7323 3.31936 48.1987 8.31506 38.967 13.3107 29.7353 24.8443 26.3013 34.076 31.297 37.3235 33.0544 39.9887 35.7196 41.746 38.967L42.315 40.01 83.043 40.01 86.233 44 46 44 46 46 87.833 46 89.443 48.013Z" stroke="black" stroke-width="1"></path><path d="M16 42.012C12.6863 42.012 10 44.6983 10 48.012 10 51.3257 12.6863 54.012 16 54.012 19.3137 54.012 22 51.3257 22 48.012 21.9896 44.7026 19.3094 42.0224 16 42.012ZM16 52.012C13.7909 52.012 12 50.2211 12 48.012 12 45.8029 13.7909 44.012 16 44.012 18.2091 44.012 20 45.8029 20 48.012 19.9983 50.2209 18.2089 52.0117 16 52.015Z" stroke="black" stroke-width="1"></path></g></svg>`,
            idm_s: `<svg id="idm_icon_s" width="19" height="20" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" overflow="hidden"><defs><clipPath id="clip_idm"><rect x="944" y="249" width="19" height="20"/></clipPath></defs><g clip-path="url(#clip_idm)" transform="translate(-944 -249)"><path d="M947.606 250 954.692 250 958.087 250 958.846 250 963 259 958.846 268 958.087 268 954.692 268 947.606 268C946.167 268 945 266.822 945 265.368L945 252.632C945 251.178 946.167 250 947.606 250Z" fill="#666666" fill-rule="evenodd"/><path d="M950.07 253.899C949.44 253.899 948.928 254.411 948.928 255.043 948.928 255.674 949.44 256.186 950.07 256.186 950.701 256.186 951.213 255.674 951.213 255.043 951.213 254.411 950.701 253.899 950.07 253.899ZM950.07 252.968C951.215 252.968 952.143 253.897 952.143 255.043 952.143 255.759 951.781 256.39 951.229 256.763L950.964 256.907 953.338 261.912 953.395 261.913C955.607 261.987 957.361 262.311 957.81 262.724L957.843 262.786 957.921 262.786 957.921 262.932 957.921 263.968 946.921 263.968 946.921 262.932 946.921 262.786 947 262.786 947.033 262.724C947.482 262.311 949.236 261.987 951.448 261.913L951.505 261.912 950.082 257.116 950.07 257.117C948.926 257.117 947.998 256.188 947.998 255.043 947.998 253.897 948.926 252.968 950.07 252.968Z" fill="#FFFFFF" fill-rule="evenodd"/></g></svg>`,
            tracker: `<svg id="tracker_icon_s" width="19" height="20" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" overflow="hidden"><defs><clipPath id="clip_tracker"><rect x="967" y="249" width="19" height="20"/></clipPath></defs><g clip-path="url(#clip_tracker)" transform="translate(-967 -249)"><rect x="968" y="250" width="6" height="6" fill="#6C6C6C"/><rect x="974" y="250" width="6" height="6" fill="#949494"/><rect x="980" y="250" width="6" height="6" fill="#6C6C6C"/><rect x="974" y="256" width="6" height="6" fill="#6C6C6C"/><rect x="974" y="262" width="6" height="6" fill="#4D4D4D"/></g></svg>`,
            datalens: `<svg width="20" height="20" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" overflow="hidden"><defs><clipPath id="clip_datalens"><rect x="2820" y="547" width="20" height="20"/></clipPath></defs><g clip-path="url(#clip_datalens)" transform="translate(-2820 -547)"><path d="M2820 549.085C2820 547.933 2820.93 547 2822.09 547L2837.92 547C2839.07 547 2840 547.933 2840 549.085L2840 564.915C2840 566.066 2839.07 567 2837.92 567L2822.09 567C2820.93 567 2820 566.066 2820 564.915Z" fill="#666666" fill-rule="evenodd"/><path d="M2823 559.708C2823 559.317 2823.32 559 2823.71 559L2825.29 559C2825.68 559 2826 559.317 2826 559.708L2826 563.292C2826 563.683 2825.68 564 2825.29 564L2823.71 564C2823.32 564 2823 563.683 2823 563.292Z" fill="#FFFFFF" fill-rule="evenodd"/><path d="M2827 555.709C2827 555.317 2827.32 555 2827.71 555L2829.29 555C2829.68 555 2830 555.317 2830 555.709L2830 563.292C2830 563.683 2829.68 564 2829.29 564L2827.71 564C2827.32 564 2827 563.683 2827 563.292Z" fill="#FFFFFF" fill-rule="evenodd"/><path d="M2831 557.708C2831 557.317 2831.32 557 2831.71 557L2833.29 557C2833.68 557 2834 557.317 2834 557.708L2834 563.292C2834 563.683 2833.68 564 2833.29 564L2831.71 564C2831.32 564 2831 563.683 2831 563.292Z" fill="#FFFFFF" fill-rule="evenodd"/><path d="M2835 552.708C2835 552.317 2835.32 552 2835.71 552L2837.29 552C2837.68 552 2838 552.317 2838 552.708L2838 563.292C2838 563.683 2837.68 564 2837.29 564L2835.71 564C2835.32 564 2835 563.683 2835 563.292Z" fill="#FFFFFF" fill-rule="evenodd"/></g></svg>`,
            certificate_s: `<svg id="wb_certified" viewBox="0 0 96 96" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" id="Icons_ShieldTick" width="20" height="20" overflow="hidden" style="" transform="translate(0,5)"><path d="M78.547 22.841C67.9406 21.9961 58.0504 17.1565 50.875 9.3 49.5224 7.73234 47.1551 7.55798 45.5874 8.91056 45.4482 9.03065 45.3181 9.16082 45.198 9.3 38.0226 17.1565 28.1324 21.9961 17.526 22.841 15.5551 23.0257 14.0531 24.6875 14.068 26.667L14.068 36.32C14.068 57.306 27.415 76.503 45.947 88.382 47.2199 89.2 48.8531 89.2 50.126 88.382 68.658 76.5 82.005 57.306 82.005 36.32L82.005 26.667C82.0199 24.6875 80.5179 23.0257 78.547 22.841ZM75.505 36.32C75.505 53.02 65.556 69.867 48.891 81.396L48.037 81.987 47.184 81.396C30.518 69.866 20.567 53.015 20.567 36.32L20.567 29.069 21.831 28.869C31.2481 27.3799 40.0132 23.1346 47.02 16.669L48.036 15.733 49.053 16.669C56.0595 23.1346 64.8242 27.3799 74.241 28.869L75.505 29.069Z" fill="#2CCC96"></path><path d="M48.036 19.788C41.0929 25.8603 32.6391 29.9454 23.567 31.612L23.567 36.32C23.567 51.747 32.694 67.383 48.037 78.33 63.378 67.385 72.505 51.748 72.505 36.32L72.505 31.612C63.4329 29.9454 54.9791 25.8603 48.036 19.788ZM45.468 58.833 35.356 48.72 38.792 45.284 45.468 51.96 59.14 38.288 62.576 41.725Z" fill="#2CCC96" style="position: relative;" transform="translate(0,0)"></path></svg>`,
            certificate_b: `<svg viewBox="0 0 96 96" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" id="Icons_ShieldTick" width="30" height="30" overflow="hidden"><path d="M78.547 22.841C67.9406 21.9961 58.0504 17.1565 50.875 9.3 49.5224 7.73234 47.1551 7.55798 45.5874 8.91056 45.4482 9.03065 45.3181 9.16082 45.198 9.3 38.0226 17.1565 28.1324 21.9961 17.526 22.841 15.5551 23.0257 14.0531 24.6875 14.068 26.667L14.068 36.32C14.068 57.306 27.415 76.503 45.947 88.382 47.2199 89.2 48.8531 89.2 50.126 88.382 68.658 76.5 82.005 57.306 82.005 36.32L82.005 26.667C82.0199 24.6875 80.5179 23.0257 78.547 22.841ZM75.505 36.32C75.505 53.02 65.556 69.867 48.891 81.396L48.037 81.987 47.184 81.396C30.518 69.866 20.567 53.015 20.567 36.32L20.567 29.069 21.831 28.869C31.2481 27.3799 40.0132 23.1346 47.02 16.669L48.036 15.733 49.053 16.669C56.0595 23.1346 64.8242 27.3799 74.241 28.869L75.505 29.069Z" fill="#2CCC96"/><path d="M48.036 19.788C41.0929 25.8603 32.6391 29.9454 23.567 31.612L23.567 36.32C23.567 51.747 32.694 67.383 48.037 78.33 63.378 67.385 72.505 51.748 72.505 36.32L72.505 31.612C63.4329 29.9454 54.9791 25.8603 48.036 19.788ZM45.468 58.833 35.356 48.72 38.792 45.284 45.468 51.96 59.14 38.288 62.576 41.725Z" fill="#2CCC96"/></svg>`,
            embeding: `<svg style="vertical-align: middle; padding:4px 6px 1px 15px; cursor: pointer;" id="CopyEmbedCodeIcon" x="0" y="0" width="20" height="20" xml:space="preserve" role="img" aria-hidden="true" style="margin-right: 6px;"><style>.prefix__st0{fill:#ddd}</style><path class="prefix__st0" d="M11.6 11.7c-.1 0-.3 0-.4-.1-.2-.2-.2-.5 0-.7l3-2.9-3-2.9c-.2-.2-.2-.5 0-.7.2-.2.5-.2.7 0l3.3 3.3c.1.1.1.2.1.4s-.1.3-.1.4l-3.3 3.3c-.1-.2-.2-.1-.3-.1zM4.5 11.7c-.1 0-.3 0-.4-.1L.8 8.2C.7 8.1.7 8 .7 7.8s.1-.3.1-.4l3.3-3.3c.3-.1.6-.1.8.1.2.2.2.5 0 .7l-3 2.9 3 2.9c.2.2.2.5 0 .7-.1.2-.3.3-.4.3zM5.9 11.7c-.1 0-.2 0-.3-.1-.2-.1-.3-.5-.2-.7l4.1-6.6c.2-.3.5-.3.7-.2.2.1.3.5.2.7l-4.1 6.6c-.1.2-.3.3-.4.3z"></path></svg>`,
            workbook_s: `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" id="Layer_1" x="0px" y="0px" width="24px" height="24px" viewBox="0 0 24 24" style="enable-background:new 0 0 24 24;" xml:space="preserve"><style type="text/css">.st0{fill:#676767;}.st1{fill:#B3B3B4;}.st2{fill:#666767;}</style><g><g><g xmlns="http://www.w3.org/2000/svg"><rect x="3" y="3" width="16" height="16" fill="#ffde40"/><path xmlns="http://www.w3.org/2000/svg" id="Square_21_" class="st0" d="M19,3H4C3.5,3,3,3.4,3,4v15c0,0.5,0.5,1,1,1h15c0.5,0,1-0.5,1-1V4C20,3.4,19.6,3,19,3z      M19,19H4V4h15V19z"/></g></g><g><rect id="Bar3_14_" x="14" y="9" class="st0" width="1" height="5"/><rect id="Bar2_14_" x="11" y="7" class="st0" width="1" height="7"/><rect id="Bar1_14_" x="8" y="10" class="st0" width="1" height="4"/></g><g><rect id="Line_4_" x="7" y="15" class="st1" width="9" height="1"/></g><rect x="20" y="5" class="st2" width="1" height="3"/><rect x="20" y="10" class="st2" width="1" height="3"/><rect x="20" y="15" class="st2" width="1" height="3"/></g></svg>`,
            bug: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-583 408.9 24 24" id="bug" width="24px" height="24px"><path d="M-566.2 415.3s.6-1.2-.7-2.4c-.8-.7-1.5-3.1-1.3-3.5.1-.4-.1-1-.3-.1-.2.8.1 2.4 1.1 3.5.6.7 1.1 1.1 1 2.2l.2.3z"></path><path fill="#331a0f" d="M-566.5 416.3s-2.8-2.7-5.8.1c0 0 2.9 1.5 1.7 4l4.1-4.1z"></path><path d="M-568.3 415.3s.8-1.1 1.8-.2c.5.5.3.9.3.9l-.4.4s-.6-.6-1.7-1.1zm2.8.7s1.2-.6 2.4.7c.8.8 3.1 1.5 3.5 1.3s1 .1.1.3c-.8.2-2.4-.1-3.5-1.1-.7-.6-1.1-1.1-2.2-.9l-.3-.3z"></path><path fill="#331a0f" d="M-566.5 416.3s2.7 2.8-.1 5.8c0 0-1.5-2.9-4-1.7l4.1-4.1z"></path><path d="M-565.5 418s1.1-.8.2-1.8c-.5-.5-.9-.3-.9-.3l-.4.4c0 .1.6.7 1.1 1.7z"></path><path fill="#010202" d="M-570.9 416.7c.3.9 1.2 1.6 1.6 2.3.3.8 1.7 1.6 2.2 1 .5-.5 1-2.4.4-3.1s1.3-.2 1 2.4-2.2 3.2-2.2 3.2-4.1-2.4-4.2-2.4c0 0-1.2-2.1-1.1-2.2 0-.1.3-1.1.3-1.1s1.7-1 2-.1z"></path><path d="M-578.6 421.5s-2.4 3.3.5 6.2c2.9 2.8 7.2.4 7.2.3-.1-.1-7.7-6.5-7.7-6.5zm7.6-1.7s-.7-1.1-1.6-1.3c0 0-.3 0-.1-.4s1.7-2.6 1.2-3.5c-.5-1-1.6-1.7-1.6-2.1s-.1-.6-.3-.5-.3.3-.3.3.1-.8-.1-.7c-.3.1 0 .7 0 .7s-.5.6.1.7c.6 0 1.6.9 1.8 1.5.1.6-.3 1.6-.6 2.3-.3.6-1.3 1.5-.4 2.2.9.8 1.8 1 1.8 1l.1-.2z"></path><path d="M-572.5 418.7s-.2-1.3-1.9-1.8c0 0-.2.1-.6.5s-1.5 1.3-2 1.3c-.5-.1-1.9-.9-1.9-.9s-.4-.6-.7-.4c-.2.2-.2.5-.2.5s-1.1-.5-.8 0 .7.3.7.3-.3.6.1.6c.4-.1.9-.3 1.2-.2s.9.4 1.3.6c.4.2.5.3.8 0s2-1.8 2-1.8.1 1.1 1 1.4l1-.1zm-3.1 1.8s-1.6-.9-2.5-.1-1.5 2.1-2 2.2c-.5 0-1.9-.5-2.1-.3-.3.2-.2.5-.2.5s-.4-.6-.5-.2c-.2.4-.1.9.1.8.2-.1.4-.3.4-.3s.1.5.5.3.7-.2 1.1-.3 1.1.1 1.3-.3c0 0 1.2-2 2-1.9s.9.8.9.8 1.2-.6 1-1.2z"></path><path fill="#e94e22" d="M-570.5 420.2l-6.9 6.9s-.3.3-1-.3c-.7-.7-1.7-3.2-.4-5.9 1.6-3.3 5-4.4 5-4.4s.9-.5 2 .2c1.1.8 1.9 2.3 1.3 3.5z"></path><path d="M-570.1 420.7s1.1.7 1.3 1.6c0 0 0 .3.4.1.4-.3 2.6-1.7 3.5-1.2 1 .5 1.7 1.6 2.1 1.6.4 0 .6.1.5.3-.1.2-.3.3-.3.3s.8-.1.7.1c-.1.3-.7 0-.7 0s-.6.5-.7-.1c0-.6-.9-1.6-1.5-1.8-.6-.1-1.6.3-2.3.6-.6.3-1.5 1.3-2.2.4-.8-.9-1-1.8-1-1.8l.2-.1z"></path><path d="M-569.4 421.7s1.3-.1 2.2 1.4c0 0 0 .3-.3.7s-1 1.8-.8 2.2c.2.4 1.2 1.7 1.2 1.7s.7.3.5.5-.4.2-.4.2.7.9.2.8-.5-.6-.5-.6-.5.4-.6 0c0-.4.1-.9-.1-1.2-.2-.3-.6-.8-.9-1.2-.3-.3-.4-.4-.2-.8.2-.3 1.3-2.4 1.3-2.4s-1.1.1-1.6-.7v-.6zm-1.2 3.4s1 1.8.2 2.7c-.8.9-2.2 1.5-2.2 2.1 0 .5.5 1.9.3 2.2-.2.3-.5.2-.5.2s.7.4.2.5c-.4.2-1 .1-.8-.1.1-.2.3-.4.3-.4s-.6-.1-.3-.6c.2-.4.2-.7.3-1.1 0-.4-.1-1.1.3-1.4 0 0 2-1.3 1.9-2-.1-.8-.7-1.1-.7-1.1s.5-1.3 1-1z"></path><path fill="#ef7a57" d="M-570.5 420.2l-6.9 6.9s-.3.5.5 1.2c.7.6 2.7 1.3 5.4.2 3.8-1.6 4.7-5 4.7-5s.5-.9-.2-2c-.8-1.1-2.3-2-3.5-1.3z"></path><path fill="#e94e22" opacity=".3" d="M-571.7 417.2s-1-1.1-2.9.5-2.3 5.4.4 4.3c1.8-.7 4.7-3.3 2.5-4.8z"></path><path fill="#331a0f" opacity=".47" d="M-570.8 417.7s1.3 2.1-3.9 6.7c0 0 4.4-4.2 6-4.3l-2.1-2.4z"></path><path fill="#d32e27" opacity=".81" d="M-568.8 420.2s.3.9-1.8 3c-1.8 1.8-5.7 2.1-7.1 3-1.5.9 1.4 2.7 2.6 2.8 4.4.3 6.5-2.4 7.3-3.7.9-1.4 1.9-3.4-1-5.1z"></path><path fill="#331a0f" opacity=".47" d="M-579.1 425.9s1 1.6 2.4.3c1.8-1.6 2.6-2.5 2.6-2.5s-2.7 2.8-3 3.7c-.3 1 1.8 1.6 1.8 1.6s-2.7 0-3.8-3.1z"></path><path fill="#f96a58" d="M-575.7 427s-2 .7-.3 1.5 4 .1 3.2-.8c-.8-1-1.7-.9-2.9-.7z" opacity=".64"></path><path fill="#ebe1e1" opacity=".35" d="M-576.9 425.9c.1.4-.4.6-1 .5s-1.1-.4-1.2-.8c-.1-.4.4-.6 1-.5s1.1.5 1.2.8z"></path></svg>`,
            taxi_logo: `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><mask id="mask0" mask-type="alpha" maskUnits="userSpaceOnUse" x="0" y="0" width="20" height="20"><path d="M10 20C15.5228 20 20 15.5228 20 10C20 4.47715 15.5228 0 10 0C4.47715 0 0 4.47715 0 10C0 15.5228 4.47715 20 10 20Z" fill="white"/></mask><g mask="url(#mask0)"><path d="M20 -0.000976562H0V9.99901H20V-0.000976562Z" fill="url(#paint0_linear)"/><path d="M20 9.99959H10V19.9996H20V9.99959Z" fill="url(#paint1_radial)"/><path d="M10 9.99959H0V19.9996H10V9.99959Z" fill="url(#paint2_linear)"/></g><defs><linearGradient id="paint0_linear" x1="0" y1="-0.000976563" x2="14.6963" y2="32.1758" gradientUnits="userSpaceOnUse"><stop stop-color="#FCE000"/><stop offset="0.47222" stop-color="#FAAA00"/><stop offset="1" stop-color="#FCE000"/></linearGradient><radialGradient id="paint1_radial" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(13.7785 28.839) rotate(-87.0199) scale(23.496)"><stop offset="0.403945" stop-color="#302F28"/><stop offset="0.566376" stop-color="#282724"/><stop offset="0.6887" stop-color="#272623"/><stop offset="0.890914" stop-color="#242321"/></radialGradient><linearGradient id="paint2_linear" x1="15.6985" y1="1.0274" x2="20.2203" y2="20.2768" gradientUnits="userSpaceOnUse"><stop stop-color="#FEFEFE"/><stop offset="0.270489" stop-color="#F9F8F7"/><stop offset="1" stop-color="#EAE3CF"/></linearGradient></defs></svg>`,
            eda_logo: `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><mask id="mask0" mask-type="alpha" maskUnits="userSpaceOnUse" x="0" y="0" width="20" height="20"><path d="M10 20C15.5228 20 20 15.5228 20 10C20 4.47715 15.5228 0 10 0C4.47715 0 0 4.47715 0 10C0 15.5228 4.47715 20 10 20Z" fill="white"/></mask><g mask="url(#mask0)"><path d="M0 0H20V20H0V0Z" fill="#FFE033"/><path d="M11.7012 15.332C13.7343 14.1581 15.1588 12.3216 15.8591 10.2362L18.0796 10.9945C17.2057 13.5952 15.4228 15.8986 12.8781 17.3677C8.51237 19.8883 3.30953 19.1636 0 16.0805V12.2823C0.04893 12.3757 0.0998942 12.4685 0.153097 12.5606C2.33307 16.3362 7.43613 17.7944 11.7012 15.332Z" fill="black"/><path d="M0 5.32329C0.615642 4.16056 1.551 3.15389 2.77039 2.44995C6.08296 0.537312 9.95575 1.72587 11.5612 4.50642C13.0661 7.11304 12.2304 10.4146 9.70417 11.8732C7.39267 13.2076 4.75037 12.3987 3.67116 10.5294C2.70253 8.85171 3.24209 6.78933 4.76846 5.908C6.11937 5.12817 7.52146 5.63129 8.04433 6.53708C8.49812 7.323 8.21921 8.11725 7.70658 8.41308C7.52533 8.51788 7.434 8.5195 7.33508 8.51625C7.37754 8.20842 7.29992 7.88471 7.09208 7.62083C6.68904 7.112 5.95225 7.02496 5.44679 7.42675C5.01312 7.77162 4.89808 8.26825 4.88729 8.59354C4.87354 8.95896 4.96979 9.33371 5.16287 9.66817C5.93312 11.0022 7.67467 11.1468 8.88233 10.4496C10.6473 9.43217 11.0844 7.12567 10.0695 5.36783C8.82729 3.21635 5.93771 2.5177 3.59273 3.87146C0.869037 5.44392 0.0747679 8.97704 1.64602 11.6986C3.42641 14.7823 7.54017 15.8364 10.8804 13.9079C14.5729 11.7759 15.7132 7.01842 13.5868 3.33537C12.7277 1.84753 11.4389 0.708212 9.93225 0H2.39522C2.12585 0.123291 1.85913 0.260824 1.59576 0.412801C1.0138 0.7487 0.481163 1.13627 0 1.56616V5.32329Z" fill="black"/></g></svg>`,
            lavka_logo: `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><mask id="mask_lavka" mask-type="alpha" maskUnits="userSpaceOnUse" x="0" y="0" width="20" height="20"><path d="M10 20C15.5228 20 20 15.5228 20 10C20 4.47715 15.5228 0 10 0C4.47715 0 0 4.47715 0 10C0 15.5228 4.47715 20 10 20Z" fill="white"/></mask><g mask="url(#mask_lavka)"><path d="M0.000488281 0H20.0005V20H0.000488281V0Z" fill="url(#paint0_linear_lavka)"/><path d="M12.5987 17.6622C12.5903 17.5742 12.5819 17.4863 12.5735 17.3942C12.1673 13.103 11.9663 10.9553 10.5049 9.49838C9.04763 8.03725 6.89946 7.83629 2.60723 7.43021C2.51929 7.42183 2.42717 7.41346 2.33923 7.40508C0.928034 7.27113 -0.0979114 5.99 0.0821523 4.58333C0.0151518 4.88896 -0.0225325 5.21133 0.0151552 5.52113C0.0905306 6.22446 0.295716 6.932 0.538592 7.47625C1.22116 9.00854 2.65329 11.4577 5.59713 14.405C8.54096 17.3482 10.9948 18.78 12.5233 19.4624C13.0677 19.7052 13.7754 19.9103 14.4789 19.9857C14.7888 20.0234 15.1112 19.9815 15.4169 19.9187C14.014 20.0988 12.7327 19.073 12.5987 17.6622Z" fill="url(#paint1_linear_lavka)"/></g><defs><linearGradient id="paint0_linear_lavka" x1="0.000488151" y1="20" x2="22.0423" y2="2.58421" gradientUnits="userSpaceOnUse"><stop stop-color="#00BFFF"/><stop offset="1" stop-color="#80FFEA"/></linearGradient><linearGradient id="paint1_linear_lavka" x1="5.95904" y1="14.295" x2="10.1493" y2="10.5209" gradientUnits="userSpaceOnUse"><stop stop-color="#E6FBFF"/><stop offset="1" stop-color="white"/></linearGradient></defs></svg>`,
            delivery_logo: `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><mask id="mask0_delivery" mask-type="alpha" maskUnits="userSpaceOnUse" x="0" y="0" width="20" height="20"><path d="M10 20C15.5228 20 20 15.5228 20 10C20 4.47715 15.5228 0 10 0C4.47715 0 0 4.47715 0 10C0 15.5228 4.47715 20 10 20Z" fill="white"/></mask><g mask="url(#mask0_delivery)"><path d="M20 0H0V20H20V0Z" fill="#F5E5CB"/><path fill-rule="evenodd" clip-rule="evenodd" d="M7.95783 20.4167H5V11.8749L16.8735 4.05293C17.0093 4.31045 17.0833 4.6007 17.0833 4.90079V13.4323C17.0833 14.0441 16.7756 14.6149 16.2645 14.9512L7.95783 20.4167Z" fill="url(#paint0_linear_delivery)"/><path fill-rule="evenodd" clip-rule="evenodd" d="M0 19.3473V8.66458L4.99996 11.875V20H0.992058L0 19.3473Z" fill="url(#paint1_linear_delivery)"/><path fill-rule="evenodd" clip-rule="evenodd" d="M11.1247 0H0V8.6645L5.00004 11.875L16.8736 4.05297C16.7326 3.78543 16.525 3.55319 16.2645 3.38183L11.1247 0Z" fill="url(#paint2_linear_delivery)"/><path fill-rule="evenodd" clip-rule="evenodd" d="M13.3333 9.06317V8.20092C13.3333 7.33004 12.8932 6.51817 12.1636 6.04275L11.4423 5.57287L11.4411 5.57208L2.88864 0H0V2.09638L9.6215 8.36496L9.62188 8.36517C9.85771 8.519 9.99996 8.78154 9.99996 9.06317V19.073L13.3333 16.8797V9.06317Z" fill="url(#paint3_linear_delivery)"/></g><defs><linearGradient id="paint0_linear_delivery" x1="4.84292" y1="15.3919" x2="17.0902" y2="15.3919" gradientUnits="userSpaceOnUse"><stop stop-color="#C9A362"/><stop offset="1" stop-color="#DCBE8A"/></linearGradient><linearGradient id="paint1_linear_delivery" x1="1.2343" y1="9.59533" x2="1.2343" y2="24.1405" gradientUnits="userSpaceOnUse"><stop stop-color="#E8C98E"/><stop offset="1" stop-color="#C79A52"/></linearGradient><linearGradient id="paint2_linear_delivery" x1="4.84358" y1="-4.1785" x2="4.84358" y2="11.8752" gradientUnits="userSpaceOnUse"><stop stop-color="#F4DEB9"/><stop offset="1" stop-color="#DCB87D"/></linearGradient><linearGradient id="paint3_linear_delivery" x1="5.69392" y1="-1.2143" x2="5.69392" y2="19.3607" gradientUnits="userSpaceOnUse"><stop stop-color="#FBF9EC"/><stop offset="1" stop-color="#EBDCBF"/></linearGradient></defs></svg>`,
            chat: `<svg width="21" height="20" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" overflow="hidden"><defs><clipPath id="clip0"><rect x="990" y="248" width="21" height="20"/></clipPath></defs><g clip-path="url(#clip0)" transform="translate(-990 -248)"><path d="M1009.05 249 991.95 249C991.422 249.003 990.997 249.45 991 249.999 991 249.999 991 249.999 991 249.999L991 262.001C990.997 262.549 991.422 262.996 991.95 262.999 991.95 262.999 991.95 262.999 991.95 262.999L1002.4 262.999 1006.2 267 1006.2 262.999 1009.05 262.999C1009.58 262.996 1010 262.549 1010 262.001 1010 262.001 1010 262.001 1010 262.001L1010 249.999C1010 249.45 1009.58 249.003 1009.05 249 1009.05 249 1009.05 249 1009.05 249ZM996.029 257.419C995.258 257.419 994.632 256.769 994.632 255.968 994.632 255.166 995.258 254.516 996.029 254.516 996.801 254.516 997.427 255.166 997.427 255.968 997.427 256.769 996.801 257.419 996.029 257.419ZM1000.5 257.419C999.728 257.419 999.103 256.769 999.103 255.968 999.103 255.166 999.728 254.516 1000.5 254.516 1001.27 254.516 1001.9 255.166 1001.9 255.968 1001.9 256.769 1001.27 257.419 1000.5 257.419ZM1004.97 257.419C1004.2 257.419 1003.57 256.769 1003.57 255.968 1003.57 255.166 1004.2 254.516 1004.97 254.516 1005.74 254.516 1006.37 255.166 1006.37 255.968 1006.37 256.769 1005.74 257.419 1004.97 257.419Z" fill="#666666" fill-rule="evenodd"/></g></svg>`,
            telegram: `<svg width="20" height="20" viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" overflow="hidden"><defs><linearGradient x1="46" y1="11" x2="29" y2="52" gradientUnits="userSpaceOnUse" id="a"><stop offset="0" stop-color="#2AABEE"/><stop offset="1" stop-color="#229ED9"/></linearGradient></defs><g transform="scale(3.47 3.47)"><circle cx="34.6" cy="34.6" r="34.6" fill="url(#a)"/><path d="M47.8 20.5C47.8 20.5 51.4 19.1 51.1 22.5 51 23.9 50.1 28.8 49.4 34.1L47 49.8C47 49.8 46.8 52.1 45 52.5 43.2 52.9 40.5 51.1 40 50.7 39.6 50.4 32.5 45.9 30 43.7 29.3 43.1 28.5 41.9 30.1 40.5L40.6 30.5C41.8 29.3 43 26.5 38 29.9L24 39.4C24 39.4 22.4 40.4 19.4 39.5L12.9 37.5C12.9 37.5 10.5 36 14.6 34.5 24.6 29.8 36.9 25 47.8 20.5Z" fill="#FFFFFF"/></g></svg>`,
            nda: `<svg width="51" height="34" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" overflow="hidden"><defs><clipPath id="clip0"><rect x="670" y="439" width="51" height="34"/></clipPath></defs><g clip-path="url(#clip0)" transform="translate(-670 -439)"><path d="M712 441 718 447 712 447Z" fill="#A6A6A6" fill-rule="evenodd"/><path d="M687.741 449.727C687.741 449.23 688.006 449 688.377 449 688.749 449 689 449.23 689 449.727L689 461.886C689 462.576 688.735 463 688.204 463 687.635 463 687.422 462.699 687.091 461.992L683.577 454.395C683.047 453.262 682.383 451.527 682.075 450.642 682.154 451.775 682.259 454.235 682.259 456.837L682.259 462.271C682.259 462.749 681.994 462.996 681.636 462.996 681.279 462.996 681 462.749 681 462.271L681 450.063C681 449.408 681.318 449 681.836 449 682.432 449 682.655 449.318 682.909 449.851L686.251 457.089C686.862 458.417 687.603 460.31 687.949 461.301 687.87 460.198 687.737 457.638 687.737 455.089Z" fill="#D9D9D9" fill-rule="evenodd"/><path d="M691 450.803C691 449.517 691.392 449 692.294 449L694.55 449C697.353 449 699 451.34 699 455.358 699 459.518 697.326 462 694.55 462L692.294 462C691.393 462 691 461.48 691 460.215ZM692.205 459.981C692.205 460.365 692.356 460.549 692.61 460.549L694.487 460.549C696.54 460.549 697.751 458.629 697.751 455.375 697.751 452.188 696.621 450.435 694.53 450.435L692.623 450.435C692.383 450.435 692.205 450.635 692.205 450.986Z" fill="#D9D9D9" fill-rule="evenodd"/><path d="M702.225 462.488C702.133 462.842 701.939 462.982 701.716 462.982 701.627 462.982 701.539 462.964 701.456 462.93 701.172 462.81 700.99 462.521 701 462.205 701.001 462.103 701.014 462.002 701.039 461.904L704.582 449.827C704.751 449.225 705.077 449 705.481 449 705.884 449 706.236 449.23 706.406 449.827L709.947 461.939C709.984 462.035 710.002 462.137 710 462.24 710.01 462.555 709.821 462.841 709.532 462.948 709.458 462.981 709.378 462.999 709.297 463 709.062 463 708.854 462.842 708.761 462.506L707.731 458.845 703.225 458.845ZM707.343 457.359 705.898 452.214C705.754 451.7 705.611 451.135 705.495 450.533 705.379 451.135 705.247 451.7 705.093 452.232L703.618 457.359Z" fill="#D9D9D9" fill-rule="evenodd"/><path d="M695.482 471.978 673.023 471.978C671.559 471.978 671 471.406 671 469.903L671 441.052C671 439.636 671.619 439.011 673.019 439.011 685.888 439.011 698.757 439.008 711.627 439.001 712.263 438.978 712.878 439.233 713.315 439.7 715.288 441.705 717.269 443.703 719.259 445.696 719.744 446.144 720.011 446.782 719.991 447.444 719.97 454.988 719.959 462.532 720 470.076 720 471.169 719.247 472.006 718.077 472 710.545 471.958 703.014 471.978 695.482 471.978ZM710.994 440.759 672.715 440.759 672.715 470.266 718.284 470.266 718.284 448.123 717.566 448.123C715.734 448.123 713.902 448.123 712.07 448.123 711.31 448.123 711 447.807 710.997 447.049 710.997 445.226 710.997 443.403 710.997 441.582ZM712.707 441.579 712.707 446.363 717.49 446.363Z" fill="#D9D9D9" fill-rule="evenodd"/></g></svg>`,
            nda_stamp: `<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFEAAABRCAMAAACdUboEAAAB+FBMVEUAAAAA//8AAP8AgL8AVaoAgL8Af78AjsYAe70AgLgAZswAgP8AebYAeLQAfr4AgLwAfb4AqqoAf78AhLkAeMMAgLsAfLsAfb4AfL4AdLkAe78AfL4AfMEAf70AccYAgL8Aeb8Afr4AfL8AfLsAer0AesIAer8AfL8Afr0AgL8Afr4AgLsAfr0AfbsAfr8Afr8Afr0Afr0AfbwAfL0Afb8Ae7kAfrwAfL0Afb4AfL8AfL4AgL0Afb8Afr4AfbwAfr0Afb4Afb4Afb4Afr0Afr4Afr0Afr4AfL8AfL8Afr0Afb4AfL8Afb8Afb0AfL8AfL4AfL4Afb8AfL0AfL8Afb4Afr0Afr4AfL8Afr4Afb4Afr0Afb8AfL8Afb8Afb0AfL8Afb4Afr8AfL8AfbwAfb4Afr8AfL4Afb0Afr4Afb4Afb4Afb8Afb8AfL4AfL0Afb4Afb0Afr4Afb8Afb4Afr0Afb0Afb4Afr4Afb0Afb4Afb4Afb8AfL4Afb4Afb4Afr0Afb0Afr0AfL8Afb8Afb8Afb0Afb4Afb4Afr4Afb8Afb0AfL4AfL4Afb4AfL4Afb4Afb8Afb4Afb4AfL4Afb4Afb4Afb0Afb4Afb4Afb4Afr4Afb4Afb0Afb8AfL4Afb4Afb0AfL4Afb4Afb4Afb0AfL4Afb4AfL6lKcctAAAAqHRSTlMAAQEEAxAICRsSBQIVEU8iOwMoHRE8KTMnCzRKJToJHCiSQEAyGTBvSSxHHowxV1tZUT1Gix1FQlZMTj5chjVVjWKBTVNlgkRUgIVzg3h/dVKPaVBekI57S2ZhYEhkcGeJY2s5fl95bEORbodYfW1qfIq6doR0cpRoelqXcbSViLNdd5Oum7u8lrKjpKipnriqrZminbWvpbCsmLmftpy9p6Chsauat6bh6YsOAAALRElEQVR4Xq3TZXuduXqG4Ut6cTEzmZmZmTm2Y3Ycs4MwYebJMOPuRmj7N+suryNJfcQwMz2/65Ye3RKnIKRVlbpuKCr/HzS/BEGa9OgRTfPwB6iGJEOQgRRWlT8kkpfwlhfkeY2wK5yvS34vGwD5dqGZrjy7xVIaCmYZ3jyXq0CTAPL3RCsqmkS4Aq1ePbV/zGgw6lMU09BUASA1ld/Cp0jVrgqbYvXwlhC6I+TNC2tSVQEMTi2/1YEw4pp814pUJWmK31RMU9cFIBROx5bT68XGASVkdtjALpMqIAWAJc+U5MvTHNMAacGRSkgAvEAO2IKQD6AIka8DSIdEmklORToQAJhg1yAK1B6E4waySBMgpQSE5AT1CWEA4LJYAiGwgicIGkA54CZD8focUgeOjJQewKwZyg2rQhEgmzUSAlkcCAmwArjAYZJmBVSJ1wAPx/C0Xs6iRjbqZinUCpL+Q7u6UhwwAPxKvQRUhSOpuXZI1QpwSzRJmlAilkjEqgrekSAArV767EffpYCDVRUKFOgAqGYiz+uPqEIVeIIuhyBzx1LaAYQsDfpBE3xIsCEQAcARU5UiABHKsvI+j6lYAWGAVABQpZQqqBxiQqm3aEbBMzPVCJ6sEKCV6hwGeigCgA5YVMAupQ0pOYzny90+qBWWWtIsMZ0PMzpUAKTmkQUQDst6PhDpXbxWAVjsK4Q1oDGLoykWAJcNrAKC1lAKfLwnz4Y5ffWaBNBsshpUp8JxlGIgjwPSmxsyEIJ3wrB+rrCAAgFWZ7OC0SI4QSnYojppapZeDhbeckvMi4+2IayTpjdzsgKJsALRAJTrQQv4yRBh6J68LUFpsaTcoPRxGuUC0AKqaqIUOzoEWWQkkvge3awEn/1ea8CEJsGpSLBYgFZJNNDgw6pxYB1Gd8YNYLvKBrQkOYFKms1/8Jb8oJaUDL6tytJIYH6+Gyu+tvx1BbOVY0mv87Ijs1SHTRcArSslDhwKABU2zl25HmZFUxYBKjleY+WDqgqFtOK3503GYrlwkN6PNjw8DkBODDbtHG/weVulUyPNcAB6w0ocipoXMt34SyjpGe7ECsgZWOYEDbOzz9tmSkjLBekQJFPk9Tab2BVgIULh2JiPzgoAyl2coHZ5u+1ydcUmkO5aMQA3Rqw3F+kDprG1t48BoUIfsM4HRGqalradmb1WmraLiktzwhoAjVAKmgabC05wpxNLL13aAJl0D1djdXKY4u0uvHh191r/tUoVIDfYlyNKGg1rEiAqsERXQkB0plohAMYUsRtPZ5gd3W5xDz4IHO4lb/nabOG5wsJ7fS2ZyOaqVSd6X467NwkoBhnFfX31xCXFBSzW1RVzoH+N9/mEdnNy9NFoX06wuLVz4+pGFdDSv3QZ7C2DD5wqECFD6+xsRYsQczDQVWZwwH+Pt5Teyfkouy9uTvoBqCgsvHixAGLVtblAfd/ScosKDnBLALWiogQlxQOFujNzQhb77IYHTwVvaVvXr6+Rc39nfA8Aubs//BJsdgQKUOpdl/u7Z9wCA6TDtekGZ9MgIotpQfaFs6Q2nFVtRVgaeWd0YuuKrs7Pv3hA2uadR492rRR3DDlLalaW7631Xw7EMQQAmiQx1Asp7qC8zL5EMAFAsBwsnTWkNfQMT6ywev3+1Uhmi9uj5xLUXp6efpDIqtkzq9ZLinP9NoTmKsgxcA1VCaKcQ39yt534leH+IAR85v0bY3eaAFAGenrGKdi6Mj9EWtXknWvNtBSeu9oZVwD5vC+nwW3FmrIbKgxWVkoSXER/+Ml5gORaLTUuo6xsomLiog1g+tZYj8mVia3rAoC8ye7qImLnNtZV0tSGhKbpZFRXrghyuI2e/bAOAFlKa5AXXWU9ZTeG/UBoZORWJZf3hy8HIDW+u7RMtG+oiXccOsIjAJzNeZIG5lFuvywDQEJ5iJyzZ+a6ysrO54AY2/+fIn9/+DUAsuZ3XqwSqu17vz+/JBz3u/YUQu4CQYw1WD/7GqbAbMJShDxz9uyZrv3MSmh7eqm9g/FbAwMKQNWV6+Nu9mb7LLwTF5RDAeAPx2CQboW6H/7q0WeB6yjbMJ2dfbZzYm6u7I7HvHH+6S4L7SO3SgD7zsTWTUneaonyfiLEFc0AUllOZIIpk/Nf/UmRV0EZg1HIuvsy+5G4dnZubsycqKs7b7Veam/fQZ/a2Bq+UgCGh/cZIFQFwBWMY8tiM8D9f5RZGezZueiCDaDuyd2XClMX9ocf7rpR1su585faR0cGesauZHEYkgzZselCy0cZovOzuRDICMBgHKoefvJkAcq79jPPj3cNk6g7v5/ZfqtN4TCEijQBsDqHfJQrUE38h9uFZOjdoP3p4cNbQGQgO3tkY27OFDfK6m5s9Sp8gA5JIAKKe9agA8hFXojukMF9YOC77x46AHE1O/vM2a4Wts8v1/NhYUiygAYorYJaYMbGjm/MT0ZjDhT99fXdbQA691s6O4EqOILFhJnKJY8CSAPFDcQT5PnqlgEQQbgP8vWTwi7SOi5cclo5WgzAqud5sO4V2cnXAZzYVq4tA7K1xAIxC4zecN/oIE3lOMkUGWR1Fyr4AaiC4ZZ6P4H2RBXALnizK+pecAopiOf2WgAtt7oaEQLAW89Cf26MYDftwy0+okOQXTY+wskk+FKIBgFFRVUp6iOkTcN6xXONne0LSB3WUlyeNTiZ6gcTcBhosc4HUMSBvHKc+ZESRIMB6HBL5VTCQDgMjQrFDc05GOVkTGKzxsbyAaisB31McAoOAOrtrhrw1dZKvGQw68MzcrEaUL0mgP25OFWgUq2QJrWcYrR8MhA70BPYiqKu29D3XwHKPcnxxJ6AhB6VAFrvUAye805c4o5PlSo4tHhVfr6nKahXlXIcJQ5oKkGrAqJjd7IeJXrov4fMwJJObikgvnLAdDdHC7QCqAVRTYlCOOEOgp/3KU2ozrb1TPv27K045ubTmqMqyfFCoC0JkYUqCJQUx8FUeB9uibnaMyQBRHaSrOUnNmbmUxwG9lg9YB9SGgAJe6OjbRYUC4fUSLLuDNlUoCpKZ1GTBWBw5F4e78tqWy0FWMq2GSUABNu2psN4FjhMKwObDRRsAx2thWSgTV3p2Z3aKw65c6v7r9/MVQEaoWW1glZgYbF5zYSYymGUN4Gsqa0NwdVOMrAAWF01vb3NOaVWAOywqsH8yowT3HMjk53gtvABpQlY/eb77DAIAGSF2bzI/+UGp0rNItCbQFTPf/LJRWg8osMOL4x3vW6qzOdA2bPP20nrh+okA9BlUL/6YvG6AmAfOV831w05DRyheRCiE599/mVm6nuPH//7PyMAX9FyE54q1dkBOBMh3gwUZU9OFaWgxMmRwquQ/+eRycXREJB89uOrJQsA/7jzZx0WnT3BCmjuA4jWfTew1G3C4iDHKHdKdOe9rpvfPgniseoPk6R9bqu9BY1/19VxEDq4bv388z8vbKjIyWKOpc/aoejTV28ef/zSCRYOfJO7eAf8AzAIUHL2iy/+/v2FPbDf93OSSK/EU/jszLdzz57NZzqkMbeDDFFz87///c2XX37fAjRNcQpG1x5YF16Pv3rz5tkXT84VpVQO2IzcjTPfvnr16ttfv9g1wDft5XQqm0yQM5/97cczjz/++KOPPvr61y+/+fznT/9596dP//WvX3766YcpAaU3nZyaaLgUAHxta7/+7c2b/838j6//6y9/efbL48ePP72bfq+BiSbBb6FWVM5aAU9i6elnPx5kfv3LVwNtIRXQG/qdkt+seP1MfykHDIfDnxSkWdrqbhfwOxVfvXuhsMgbEQCIZLhkra5srYA/xhLrvj2S/fT2uQsjj2Zj+ZzkfwA2RdXDZM7sFwAAAABJRU5ErkJggg==" />`,
            stat: `<svg width="18" height="19" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" overflow="hidden"><defs><clipPath id="clip0"><rect x="1069" y="247" width="18" height="19"/></clipPath></defs><g clip-path="url(#clip0)" transform="translate(-1069 -247)"><path d="M1086 249.751C1086 248.785 1085.2 248.001 1084.22 248 1083.24 247.999 1082.44 248.782 1082.44 249.748 1082.44 250.341 1082.74 250.893 1083.25 251.216L1081.93 255.001 1081.93 255.001C1081.56 255 1081.21 255.109 1080.91 255.313L1078.25 253.356C1078.59 252.449 1078.12 251.443 1077.2 251.108 1076.28 250.774 1075.25 251.237 1074.91 252.144 1074.63 252.901 1074.91 253.75 1075.59 254.201L1073.89 259.5 1073.79 259.5C1072.8 259.498 1072 260.28 1072 261.246 1072 262.212 1072.79 262.998 1073.78 263 1074.76 263.002 1075.56 262.221 1075.56 261.254 1075.56 260.701 1075.3 260.179 1074.85 259.848L1076.56 254.501 1076.58 254.501C1076.97 254.5 1077.34 254.379 1077.64 254.156L1080.28 256.093C1080.19 256.302 1080.15 256.525 1080.15 256.751 1080.15 257.717 1080.94 258.501 1081.93 258.501 1082.91 258.501 1083.71 257.718 1083.71 256.752 1083.71 256.162 1083.41 255.612 1082.91 255.288L1084.22 251.501C1085.2 251.501 1086 250.718 1086 249.751Z" fill="#666666" fill-rule="evenodd"/><path d="M1071.48 248 1070 248 1070 265 1087 265 1087 263.543 1071.48 263.543 1071.48 248Z" fill="#666666" fill-rule="evenodd"/></g></svg>`,
            info: `<svg version="1.1" id="info_icon" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="19px" height="19px" viewBox="0 0 15 15" style="enable-background:new 0 0 15 15;" xml:space="preserve"><path id="Circle_4_" style="opacity:0.8;fill:#FFFFFF;" d="M7.5,1C3.9,1,1,3.9,1,7.5S3.9,14,7.5,14S14,11.1,14,7.5S11.1,1,7.5,1z M7.5,13 C4.5,13,2,10.5,2,7.5S4.5,2,7.5,2S13,4.5,13,7.5S10.5,13,7.5,13z"/><rect id="ILine" x="6.9" y="6" style="opacity:0.8;fill:#FFFFFF;" width="1.3" height="5"/><rect id="IDot" x="6.9" y="3.9" style="opacity:0.8;fill:#FFFFFF;" width="1.3" height="1.3"/></svg>`
          },
          css : `
            .flex-container {
                display: flex;
            }

            .flex-child {
                flex-wrap: wrap;
                margin: 15px 25px 2px 5px;
                width: 300px;
            }

            [class*="Breadcrumbs_container_"] {
                line-height: 32px;
                height: 24px;
            }

            .Home_page-header_fdt2na2 {
              margin-bottom: 25px;
              display: none;
            }

            .Home_root_f1h6if9w {
              margin: 9px 24px 0;
            }

            #TableauSupport {
                position: absolute;
                bottom: 0;
                left: 0;
                border: 1px solid #ccc;
                width:28px;
                height:66px;
                margin:2px;
                background-color:#fff;
            }

            #TableauSupport .icon_container{
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                height:28px;
            }

            #TableauNDA{
                position: absolute;
                bottom: -30px;
                right: -25px;
            }

            @media (max-width: 1100px) {
                #wiki-embed {
                    display: none;
                }

            }

            @media (max-width: 1400px) {
                #wiki-embed-text {
                    display: none;
                }

            }

            .tippy-content a {
                color: #1a699e;
            }

            .tippy-content a:hover {
                color: #2a79af;
            }

            /*Tippy Light Theme*/
            .tippy-box[data-theme~=light-border]{background-color:#fff;background-clip:padding-box;border:1px solid rgba(0,8,16,.15);color:#333;box-shadow:0 4px 14px -2px rgba(0,8,16,.08)}.tippy-box[data-theme~=light-border]>.tippy-backdrop{background-color:#fff}.tippy-box[data-theme~=light-border]>.tippy-arrow:after,.tippy-box[data-theme~=light-border]>.tippy-svg-arrow:after{content:"";position:absolute;z-index:-1}.tippy-box[data-theme~=light-border]>.tippy-arrow:after{border-color:transparent;border-style:solid}.tippy-box[data-theme~=light-border][data-placement^=top]>.tippy-arrow:before{border-top-color:#fff}.tippy-box[data-theme~=light-border][data-placement^=top]>.tippy-arrow:after{border-top-color:rgba(0,8,16,.2);border-width:7px 7px 0;top:17px;left:1px}.tippy-box[data-theme~=light-border][data-placement^=top]>.tippy-svg-arrow>svg{top:16px}.tippy-box[data-theme~=light-border][data-placement^=top]>.tippy-svg-arrow:after{top:17px}.tippy-box[data-theme~=light-border][data-placement^=bottom]>.tippy-arrow:before{border-bottom-color:#fff;bottom:16px}.tippy-box[data-theme~=light-border][data-placement^=bottom]>.tippy-arrow:after{border-bottom-color:rgba(0,8,16,.2);border-width:0 7px 7px;bottom:17px;left:1px}.tippy-box[data-theme~=light-border][data-placement^=bottom]>.tippy-svg-arrow>svg{bottom:16px}.tippy-box[data-theme~=light-border][data-placement^=bottom]>.tippy-svg-arrow:after{bottom:17px}.tippy-box[data-theme~=light-border][data-placement^=left]>.tippy-arrow:before{border-left-color:#fff}.tippy-box[data-theme~=light-border][data-placement^=left]>.tippy-arrow:after{border-left-color:rgba(0,8,16,.2);border-width:7px 0 7px 7px;left:17px;top:1px}.tippy-box[data-theme~=light-border][data-placement^=left]>.tippy-svg-arrow>svg{left:11px}.tippy-box[data-theme~=light-border][data-placement^=left]>.tippy-svg-arrow:after{left:12px}.tippy-box[data-theme~=light-border][data-placement^=right]>.tippy-arrow:before{border-right-color:#fff;right:16px}.tippy-box[data-theme~=light-border][data-placement^=right]>.tippy-arrow:after{border-width:7px 7px 7px 0;right:17px;top:1px;border-right-color:rgba(0,8,16,.2)}.tippy-box[data-theme~=light-border][data-placement^=right]>.tippy-svg-arrow>svg{right:11px}.tippy-box[data-theme~=light-border][data-placement^=right]>.tippy-svg-arrow:after{right:12px}.tippy-box[data-theme~=light-border]>.tippy-svg-arrow{fill:#fff}.tippy-box[data-theme~=light-border]>.tippy-svg-arrow:after{background-image:url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iNiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMCA2czEuNzk2LS4wMTMgNC42Ny0zLjYxNUM1Ljg1MS45IDYuOTMuMDA2IDggMGMxLjA3LS4wMDYgMi4xNDguODg3IDMuMzQzIDIuMzg1QzE0LjIzMyA2LjAwNSAxNiA2IDE2IDZIMHoiIGZpbGw9InJnYmEoMCwgOCwgMTYsIDAuMikiLz48L3N2Zz4=);background-size:16px 6px;width:16px;height:6px}
            .tippy-box {border-radius: 0px;}

            /*jquery.toasts.js*/
            .jq-toast-wrap { display: block; position: fixed; width: 250px;  pointer-events: none !important; margin: 0; padding: 0; letter-spacing: normal; z-index: 9000 !important; }
            .jq-toast-wrap * { margin: 0; padding: 0; }
            
            .jq-toast-wrap.bottom-left { bottom: 20px; left: 20px; }
            .jq-toast-wrap.bottom-right { bottom: 20px; right: 80px; }
            .jq-toast-wrap.top-left { top: 20px; left: 20px; }
            .jq-toast-wrap.top-right { top: 20px; right: 40px; }
            
            .jq-toast-single { display: block; width: 100%; padding: 10px; margin: 0px 0px 5px; border-radius: 4px; font-size: 12px; font-family: arial, sans-serif; line-height: 17px; position: relative;  pointer-events: all !important; background-color: #444444; color: white; }
            
            .jq-toast-single h2 { font-family: arial, sans-serif; font-size: 14px; margin: 0px 0px 7px; background: none; color: inherit; line-height: inherit; letter-spacing: normal; }
            .jq-toast-single a { color: #eee; text-decoration: none; font-weight: bold; border-bottom: 1px solid white; padding-bottom: 3px; font-size: 12px; }
            
            .jq-toast-single ul { margin: 0px 0px 0px 15px; background: none; padding:0px; }
            .jq-toast-single ul li { list-style-type: disc !important; line-height: 17px; background: none; margin: 0; padding: 0; letter-spacing: normal; }
            
            .close-jq-toast-single { position: absolute; top: 3px; right: 7px; font-size: 14px; cursor: pointer; }
            
            .jq-toast-loader { display: block; position: absolute; top: -2px; height: 5px; width: 0%; left: 0; border-radius: 5px; background: red; }
            .jq-toast-loaded { width: 100%; }
            .jq-has-icon { padding: 10px 10px 10px 50px; background-repeat: no-repeat; background-position: 10px; }
            .jq-icon-info { background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGwSURBVEhLtZa9SgNBEMc9sUxxRcoUKSzSWIhXpFMhhYWFhaBg4yPYiWCXZxBLERsLRS3EQkEfwCKdjWJAwSKCgoKCcudv4O5YLrt7EzgXhiU3/4+b2ckmwVjJSpKkQ6wAi4gwhT+z3wRBcEz0yjSseUTrcRyfsHsXmD0AmbHOC9Ii8VImnuXBPglHpQ5wwSVM7sNnTG7Za4JwDdCjxyAiH3nyA2mtaTJufiDZ5dCaqlItILh1NHatfN5skvjx9Z38m69CgzuXmZgVrPIGE763Jx9qKsRozWYw6xOHdER+nn2KkO+Bb+UV5CBN6WC6QtBgbRVozrahAbmm6HtUsgtPC19tFdxXZYBOfkbmFJ1VaHA1VAHjd0pp70oTZzvR+EVrx2Ygfdsq6eu55BHYR8hlcki+n+kERUFG8BrA0BwjeAv2M8WLQBtcy+SD6fNsmnB3AlBLrgTtVW1c2QN4bVWLATaIS60J2Du5y1TiJgjSBvFVZgTmwCU+dAZFoPxGEEs8nyHC9Bwe2GvEJv2WXZb0vjdyFT4Cxk3e/kIqlOGoVLwwPevpYHT+00T+hWwXDf4AJAOUqWcDhbwAAAAASUVORK5CYII='); background-color: #31708f; color: #d9edf7; border-color: #bce8f1; }
            .jq-icon-warning { background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGYSURBVEhL5ZSvTsNQFMbXZGICMYGYmJhAQIJAICYQPAACiSDB8AiICQQJT4CqQEwgJvYASAQCiZiYmJhAIBATCARJy+9rTsldd8sKu1M0+dLb057v6/lbq/2rK0mS/TRNj9cWNAKPYIJII7gIxCcQ51cvqID+GIEX8ASG4B1bK5gIZFeQfoJdEXOfgX4QAQg7kH2A65yQ87lyxb27sggkAzAuFhbbg1K2kgCkB1bVwyIR9m2L7PRPIhDUIXgGtyKw575yz3lTNs6X4JXnjV+LKM/m3MydnTbtOKIjtz6VhCBq4vSm3ncdrD2lk0VgUXSVKjVDJXJzijW1RQdsU7F77He8u68koNZTz8Oz5yGa6J3H3lZ0xYgXBK2QymlWWA+RWnYhskLBv2vmE+hBMCtbA7KX5drWyRT/2JsqZ2IvfB9Y4bWDNMFbJRFmC9E74SoS0CqulwjkC0+5bpcV1CZ8NMej4pjy0U+doDQsGyo1hzVJttIjhQ7GnBtRFN1UarUlH8F3xict+HY07rEzoUGPlWcjRFRr4/gChZgc3ZL2d8oAAAAASUVORK5CYII='); background-color: #c89423; color: #fcf8e3; border-color: #faebcc; }
            .jq-icon-error { background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAHOSURBVEhLrZa/SgNBEMZzh0WKCClSCKaIYOED+AAKeQQLG8HWztLCImBrYadgIdY+gIKNYkBFSwu7CAoqCgkkoGBI/E28PdbLZmeDLgzZzcx83/zZ2SSXC1j9fr+I1Hq93g2yxH4iwM1vkoBWAdxCmpzTxfkN2RcyZNaHFIkSo10+8kgxkXIURV5HGxTmFuc75B2RfQkpxHG8aAgaAFa0tAHqYFfQ7Iwe2yhODk8+J4C7yAoRTWI3w/4klGRgR4lO7Rpn9+gvMyWp+uxFh8+H+ARlgN1nJuJuQAYvNkEnwGFck18Er4q3egEc/oO+mhLdKgRyhdNFiacC0rlOCbhNVz4H9FnAYgDBvU3QIioZlJFLJtsoHYRDfiZoUyIxqCtRpVlANq0EU4dApjrtgezPFad5S19Wgjkc0hNVnuF4HjVA6C7QrSIbylB+oZe3aHgBsqlNqKYH48jXyJKMuAbiyVJ8KzaB3eRc0pg9VwQ4niFryI68qiOi3AbjwdsfnAtk0bCjTLJKr6mrD9g8iq/S/B81hguOMlQTnVyG40wAcjnmgsCNESDrjme7wfftP4P7SP4N3CJZdvzoNyGq2c/HWOXJGsvVg+RA/k2MC/wN6I2YA2Pt8GkAAAAASUVORK5CYII='); background-color: #a94442; color: #f2dede; border-color: #ebccd1; }
            .jq-icon-success { background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAADsSURBVEhLY2AYBfQMgf///3P8+/evAIgvA/FsIF+BavYDDWMBGroaSMMBiE8VC7AZDrIFaMFnii3AZTjUgsUUWUDA8OdAH6iQbQEhw4HyGsPEcKBXBIC4ARhex4G4BsjmweU1soIFaGg/WtoFZRIZdEvIMhxkCCjXIVsATV6gFGACs4Rsw0EGgIIH3QJYJgHSARQZDrWAB+jawzgs+Q2UO49D7jnRSRGoEFRILcdmEMWGI0cm0JJ2QpYA1RDvcmzJEWhABhD/pqrL0S0CWuABKgnRki9lLseS7g2AlqwHWQSKH4oKLrILpRGhEQCw2LiRUIa4lwAAAABJRU5ErkJggg=='); color: #dff0d8; background-color: #3c763d; border-color: #d6e9c6; }
          `,
          selectors :{
            loginInput: `[tb-test-id="textbox-username-input"]`,
            datagrid_project_owner: `[data-tb-test-id*="list-owner-cell-project-"] > a`,
            datagrid_workbook_owner: `[data-tb-test-id*="list-owner-cell-workbook-"] > a`,
            datagrid_view_owner: `[data-tb-test-id*="list-owner-cell-view-"] > a`,
            page_header_owner: `[data-tb-test-id*="space-header-owner"]`,
            page_header: `div.tb-main-content > div:first-child`, //`[class*="PageHeader_container_"]`,
            page_title: `[data-tb-test-id="space-header-name"]`,
            viewpage_favorite_button: `[class*="tb-favorite-button-light"]`,
            viewpage_breadcrumb_workbook: `[data-tb-test-id*="breadcrumb-workbook-"]`,            
          },
          logging : true

  };

  var TabUIAPI = new function (){
    //API Requests
    var 
        endpoints = {
        "IDMintegration"   : "https://dwh-idm-integration.taxi.yandex-team.ru",
        "Vizportal"         : "https://tableau.taxi.yandex-team.ru/vizportal/api/web/v1",
        "GraphQL"          :  "https://tableau.taxi.yandex-team.ru/relationship-service-war/graphql",
        "Suggest"           : "https://search.yandex-team.ru/suggest",
        },
        headers = {
            Vizportal: {
                "accept": "application/json",
                "content-type": "application/json!",
                "x-xsrf-token": Cookies.get("XSRF-TOKEN"),
            }
        }

    this._hasError = (obj) => {
      return obj.hasOwnProperty("errors");
    }

    this.fetchGraphQL = async (method, param = "") => {
        /*
          Usage:
          request_graphql ('getWorkbookExtracts', '6519').then(data => {
          console.log(data)
          });
          */
        body_list = {
          getWorkbookExtracts: `{\"query\":\"{\\n  workbooks(filter: {vizportalUrlId:\\\"${param}\\\"}) {\\n    name\\n    # Published\\n    upstreamDatasources{\\n      name\\n      extractLastUpdateTime\\n      extractLastRefreshTime\\n      extractLastIncrementalUpdateTime\\n      hasExtracts\\n    }\\n    # Embedded\\n    embeddedDatasources{\\n      name\\n      extractLastUpdateTime\\n      extractLastRefreshTime\\n      extractLastIncrementalUpdateTime\\n      hasExtracts\\n    }\\n  }\\n}\",\"variables\":null,\"operationName\":null}`,
        };
        try {
          const response = await fetch(endpoints.GraphQL, {
            headers: headers.Vizportal,
            body: body_list[method],
            method: "POST",
            mode: "cors",
            credentials: "include",
          });
          const data = await response.json();
          return data;
        } catch (error) {
          return console.log(error);
        }
    };

    this.fetchYandexSearch = async (searchword, layers = "people,services") => {
        /*
          Usage:
          request_yasearch ('shevtsoff').then(data => {
          console.log(data)
          });
          */
        try {
          const response = await fetch(
            `${endpoints.Suggest}/?text=${searchword}&version=2&language=ru&feature.get_user_gaps=1&feature.enable_highlight_suggest=1&layers=${layers}`,
            {
              headers: {
                accept: "*/*",
                "accept-language": "ru,en;q=0.9,es;q=0.8",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
              },
              referrerPolicy: "strict-origin-when-cross-origin",
              body: null,
              method: "GET",
              mode: "cors",
              credentials: "include",
            }
          );
          const data = await response.json();
          return data;
        } catch (error) {
          return console.log(error);
        }
      };

    this.fetchTracker = async (method, params) => {
    /*
        data = await request_tracker('issues','filter=queue:TABL,TAXIREPORTING,TAXIANALYTICS&filter=reportID:3919');
        console.log(data);
        */
    try {
        const response = await fetch(
        `${endpoints.IDMintegration}/tracker_api/${method}?${params}`
        );
        const data = await response.json();
        return data;
    } catch (error) {
        return console.log(error);
    }
    };

    this.fetchIDM = async (method, params) => {
    /*
        data = await request_idm('roles','system=taxi-dwh-idm-integration&type=active&path=/tableau_analyst/license/creator/');
        console.log(data);
        */
    try {
        const response = await fetch(
        `${endpoints.IDMintegration}/idm_api/${method}/?${params}&limit=1000`
        );
        const data = await response.json();
        return data.objects;
    } catch (error) {
        return console.log(error);
    }
    };

    this.fetchStaff = async (method, params) => {
    /*
        request_staff('persons','_query=department_group.ancestors.level==4&login=shevtsoff&_pretty=1&_fields=department_group.ancestors.name,department_group.ancestors.level,login').then(data=>{
        console.log(data);
        });
        */
    try {
        const response = await fetch(
        `${endpoints.IDMintegration}/staff_api/${method}?${params}`
        );
        const data = await response.json();
        return data;
    } catch (error) {
        return console.log(error);
    }
    };

    this.fetchVizPortal = async (method, param = "") => {
        console.log("[TabUIAPI.fetchVizPortal] — ", method);
        /*
        Usage:
        fetchVizPortal('getWorkbook', '6519').then(data => {
        console.log(data)
        });
        fetchVizPortal('getViewByPath', 'UserDebts/UserDebts')
        */
        const bodyList = {
            'getViewByPath'             : {"method":"getViewByPath","params":{"path": param}},
            'getWorkbook'               : {"method":"getWorkbook","params":{"id": param}},
            'getProjectAncestors'       : {"method":"getProjectAncestors","params":{"id": param}},
            'getProjects'               : {"method":"getProjects","params":{"filter":{"operator":"and","clauses":[{"operator":"eq","field":"parentProjectId","value":param}]},"page":{"startIndex":0,"maxItems":500}}}, // получить все папки дочерние по отношению к заданной
            'getUsersGroupMembership'   : {"method":"getUsersGroupMembership","params":{"userIds":[param]}},
            'getDatasourceById'         : {"method":"getDatasource","params":{"id": param}},
            'getDatasources'            : {"method":"getDatasources","params":{"filter":{"operator":"and","clauses":[{"operator":"eq","field":"workbookId","value":param}]},"order":[{"field":"name","ascending":true}],"page":{"startIndex":0,"maxItems":100},"statFields":["hitsTotal","hitsLastOneMonthTotal","hitsLastThreeMonthsTotal","hitsLastTwelveMonthsTotal","connectedWorkbooksCount"]}},
            'getWorkbooksByTag'         : {"method":"getWorkbooks","params":{"filter":{"operator":"and","clauses":[{"operator":"has","field":"tags","value": param}]},"order":[{"field":"name","ascending":true}],"page":{"startIndex":0,"maxItems":600},"statFields":["hitsTotal","favoritesTotal","hitsLastOneMonthTotal","hitsLastThreeMonthsTotal","hitsLastTwelveMonthsTotal","subscriptionsTotal"]}},
            'getUserByLogin'            : {"method":"getSiteUsers","params": {"filter": {"operator": "and","clauses": [{"operator": "eq","field": "username","value": param},{"operator": "eq","field": "domainName","value": "ld.yandex.ru"}]},"page": {"startIndex": 0,"maxItems": 1}}},
            'getUsersByRoleName'        : {"method":"getSiteUsers","params":{"filter":{"operator":"and","clauses":[{"operator":"eq","field":"siteRole","value": param}]},"order":[{"field":"displayName","ascending":true}],"page":{"startIndex":0,"maxItems":600}}},
            'getUsersByGroupId'         : {"method":"getSiteUsers","params":{"filter":{"operator":"and","clauses":[{"operator":"has","field":"groupIds","value": param}]},"order":[{"field":"displayName","ascending":true}],"page":{"startIndex":0,"maxItems":100}}},
            'getSessionInfo'            : {"method":"getSessionInfo","params":{}},
            'getGroupById'              : {"method":"getGroups","params":{"filter":{"operator":"and","clauses":[{"operator":"eq","field":"id","value": param}]},"page":{"startIndex":0,"maxItems":1}}},
            'getADgroups'               : {"method":"searchActiveDirectoryGroupName","params":{"name":"*tableau-*"}},
            'addADgroup'                : {"method":"syncActiveDirectoryGroup","params":{"name":param,"domainName":"ld.yandex.ru","siteRole":"Unlicensed","grantLicenseMode":"on-sync"}},
            'deleteNestedPermissions'   : {"method":"setContentControlledPermissions","params":{"ids":[param],"nestedProjectsPermissionsIncluded":false}}
        };
        try {
                const response = await fetch(
                `${endpoints.Vizportal}/${bodyList[method]["method"]}`,
                {
                    headers: headers.Vizportal,
                    body: JSON.stringify(bodyList[method]),
                    method: "POST",
                    mode: "cors",
                    credentials: "include",
                }
                );
                const data = await response.json();
                return data.result;
            } catch (error) {
                return console.warn(error);
            }
    };

    this.getNews = async (groups) => {
        payload = {
          login: Cookies.get("yandex_login"),
          groups: groups,
        };
        try {
          
          const response = await fetch(
            `${endpoints.IDMintegration}/tableau_api/getNews`,
            {
              body: JSON.stringify(payload),
              method: "POST",
            }
          );
          const data = await response.json();
          console.log("[TabUIAPI.getNews] - fetched:", data);
          return data;
        } catch (error) {
          return console.log(error);
        }
    };

    this.getUserIDMRoles = async (user_login) => {
        /*
          Used for storing user metadata to localstorage
          */
        try {
          const response = await fetch(`${endpoints.IDMintegration}/role-info-from-idm/?yandex_passport_login=${user_login}`);
          const data = await response.json();
          console.log("[TabUIAPI.getUserIDMRoles] - fetched:", data);
          return data;
        } catch (error) {
          return console.log(error);
        }
    };

    this.getPromotedWorkbooks = async () => {
        /*
          Used in homepage for showing Main Reports
          */
        try {
          const response = await fetch(`${endpoints.IDMintegration}/tableau_api/getPromotedWorkbooks`);
          const data = await response.json();
          console.log("[TabUIAPI.getPromotedWorkbooks] - fetched:", data);
          return data;
        } catch (error) {
          return console.log(error);
        }
    };

    this.getWorkbookAlert = async (wb_id) => {
        /*
        Returns data for workbook alert. Data is stored in "snb_tableau.dm_tableau_announces_manual_act" table
        For details visit: https://wiki.yandex-team.ru/taxi/analytics/tools/tableau/server/services/custom-js-alerts/
        :return: json
          */
        try {
            const response = await fetch(`${endpoints.IDMintegration}/tableau_api/getWorkbookAlert?workbook_id=${wb_id}`);
            const data = await response.json();
            console.log("[TabUIAPI.getWorkbookAlert] - fetched:", data);
            return data;
        } catch (error) {
            return console.log(error);
        }
    };

    this.getWorkbookId = async (path, type) => {
        /* Returns workbook_id and owner based on path and type parsed from url
        :return: json 
        {
            "workbook_id": "6519",
            "workbook_owner": "alexbalonin"
        }
        */
        //console.log("Making request to IDM integration:", path, type);
        try {
            const response = await fetch(`${endpoints.IDMintegration}/tableau_api/getWorkbookId?path=${path}&type=${type}`);
            const data = await response.json();
            //console.log(`Workbook_id based in IDM: ${data["workbook_id"]}`);
            console.log("[TabUIAPI.getWorkbookId] - fetched:", data);
            return data;
        } catch (error) {
            return console.log(error);
        }
    };

    this.getWorkbookMeta = async (wb_id) => {
        /* Returns workbook metadata based on it's ID
          :return: json
          */
        try {
          const data = await this.fetchVizPortal("getWorkbook", wb_id);
          if (data.project != null) {
            //Enrich current_wb_meta with projects info
            project_id = await data.project.id;
            const projects = await this.fetchVizPortal("getProjectAncestors", project_id);
            wb_projects = await projects["projects"];
            data.projects = await wb_projects;
            data.projectPath = await wb_projects.map((e) => e.name).join(" → ");
          }
      
          //Enrich current_wb_meta with datasources info
          const datasources = await this.fetchVizPortal("getDatasources", wb_id);
          data.datasources = await datasources.datasources;
      
          data.datasources.map((ds) => {
            if (ds.hasExtracts) {
              data.datasourcesLastRefresh = new Date(ds.connectionDetails.lastRefreshedAt || ds.lastRefreshedAt).toLocaleString();
            } else {
              if (ds.connectionDetails.lastRefreshedAt || ds.lastRefreshedAt) {
                data.datasourcesLastRefresh = new Date(ds.connectionDetails.lastRefreshedAt || ds.lastRefreshedAt).toLocaleString();
              } else {
              }
            }
          });
          console.log("[TabUIAPI.getWorkbookMeta] - fetched:", data);
          return data;
        } catch (error) {
          return console.log(error);
        }
    };

  }

  var TabUIMeta = new function (){

    this.setCertifiedWorkbooks = async () => {
      const data = await TabUIAPI.fetchVizPortal("getWorkbooksByTag", "certified:yes");
      TabUI.context.certifiedWorkbooks = data ? data["workbooks"].map((wb) => wb.id) : [];
      localStorage.setItem("certifiedWorkbooks", JSON.stringify(TabUI.context.certifiedWorkbooks));
      console.log("[TabUIMeta.setCertifiedWorkbooks] — set:", TabUI.context.certifiedWorkbooks);
    };
  
    this.setCurrentUser = async () => {
      const data = await TabUIAPI.fetchVizPortal("getSessionInfo");
      if (data) {
        // Storing Permission meta from Tableau to current_user_meta
        let userID = await data.user.id;
        const groups = await TabUIAPI.fetchVizPortal("getUsersGroupMembership", userID);
        userGroups = await groups.groups;
        data.user.groups = await userGroups;
        data.user.group_list = await userGroups.map((e) => e.name);
    
        // Storing Permission meta from IDM to current_user_meta
        userLogin = await data.user.username;
        const idm = await TabUIAPI.getUserIDMRoles(userLogin);
        data.user.idmRoles = await idm;
    
        // Storing News for current_user
        const news = await TabUIAPI.getNews(data.user.group_list);
        data.user.news = await news;
    
        //Storing meta
        TabUI.context.currentUserMeta = await data.user;
        localStorage.setItem("currentUserMeta", JSON.stringify(TabUI.context.currentUserMeta));
        console.log("[TabUIMeta.setCurrentUser] — set:", TabUI.context.currentUserMeta);
      }
    };
  
  }

  //============================= Renderings =========================================
  var TabUIRender = new function (){

    this.renderPage = () => {
      this.clearInnerHTML("tabui-alert");
      console.log('[TabUIRender.renderPage] - current directory: ', TabUI.context.currentDirectory.name, window.location.hash);
      //set_css(TabUI.css);
      this.renderSignInErrors();
      //Page renderings
      this.renderSupportButtons();
      this.observeSidePanelClick();
      
      this.renderNDA();

      if (TabUI.context.currentDirectory.name == 'home'){
        this.renderPromotedWorkbooks();
        this.renderSearchReports();
      }
      if (TabUI.context.currentDirectory.name == 'explore'){


      }
      if (TabUI.context.currentDirectory.name == 'favorites'){
        TabUIRender.renderWorkbooksCertifiedIcon(TabUI.context.certifiedWorkbooks);
        this._mutationsEnded().then(() => TabUIRender.renderWorkbooksCertifiedIcon(TabUI.context.certifiedWorkbooks));

      }
      if (TabUI.context.currentDirectory.name == 'project'){
          this.clearInnerHTML("wb_subtitle"); //Заплатка. SubTitle пролезал на другие страницы
          this._mutationsEnded().then(() => TabUIRender.renderWorkbooksCertifiedIcon(TabUI.context.certifiedWorkbooks));
      }
      if (TabUI.context.currentDirectory.name == 'workbook'){
          //let workbookID = window.location.hash.replace("#/workbooks/", "").split("?")[0].split("/")[0];
          let workbookID = TablUILocator().hashParts.id
          TabUIAPI.getWorkbookId(workbookID, 'workbook').then((checkedWorkbookData) => {
            if (_.isEmpty(checkedWorkbookData)) {
              workbook_id = null;
              workbook_owner = null;
            } else {
              workbook_id = checkedWorkbookData.workbook_id;
              workbook_owner = checkedWorkbookData.workbook_owner;
            }
            window.current_wb_id = workbook_id;
      
            this._mutationsEnded().then(() => {
              this.renderErrorPage(checkedWorkbookData);
              this.clearInnerHTML("wb_subtitle");
            });
            if (workbook_id) {
              this.renderAlerts(workbook_id);
              this.renderWorkbookID(workbook_id);
              TabUIAPI.getWorkbookMeta(workbook_id).then((wbMeta) => {
                //adding info about review ticket to meta
                if (wbMeta) {
                  //If you don't have permissions to workbook, you won't fetch it's meta
                  wbMeta.review_ticket = this.getTagValue(
                    wbMeta["tags"],
                    "review_ticket"
                  );
                  //window.current_wb_meta = wb_meta;
                  TabUI.context.currentWorkbookMeta = wbMeta;
                  this.renderDownloadButton(wbMeta);
                  if (!TabUIAPI._hasError(wbMeta)) {
                    this.renderWorkbookCertifiedIcon(wbMeta);
                    this.renderIDMButton(wbMeta);
                    this.renderTrackerButton(wbMeta);
                    this.renderDatalensButton(wbMeta);
                    this.renderWorkbookStatButton(wbMeta);
                  }
                }
                //enrich_wb_meta(workbook_id);
              });
            } else {
              console.log("Workbook ID is NULL");
            }
          });

      }
      if (TabUI.context.currentDirectory.name == 'view'){
        let viewPathSheets = TabUI.context.currentDirectory.id + '/sheets/' + TabUI.context.currentDirectory.subDirectory
        let viewPath = TabUI.context.currentDirectory.id + '/' + TabUI.context.currentDirectory.subDirectory
        console.log('viewPath', viewPath)
        TabUIAPI.getWorkbookId(viewPathSheets, 'view').then((checked_wb_data) => {
          //checked_wb_data = {"workbook_id":8559,"workbook_luid":"06e3fb14-d29b-48ce-a5e5-c2a68d41fbc2","workbook_name":"Postcards Events","workbook_owner":"natalyazorina"}
            if (_.isEmpty(checked_wb_data)) {
              workbook_id = null;
              workbook_owner = null;
            } else {
              workbook_id = checked_wb_data.workbook_id;
              workbook_owner = checked_wb_data.workbook_owner;
            }
            window.current_wb_id = workbook_id;
            this.renderWikiEmbedButton();
            this._mutationsEnded().then(() => {
              this.renderErrorPage(checked_wb_data);
            });
            if (workbook_id) {
              // Means WB exists
              this.renderAlerts(workbook_id);
              TabUIAPI.getWorkbookMeta(current_wb_id).then((wb_meta) => {
                  //adding info about review ticket to meta
                  wb_meta.review_ticket = this.getTagValue(wb_meta["tags"], "review_ticket");
                  //window.current_wb_meta = wb_meta;
                  TabUI.context.currentWorkbookMeta = wb_meta;
                  // enrich_wb_meta(workbook_id).then(data => {});
                  return wb_meta;
                })
                .then((wb_meta) => {
                  this.renderViewCertifiedIcon(wb_meta);
                  this.renderSubtitle(wb_meta);
                  this.renderViewWorkbookID(wb_meta);
                  this.renderWorkbookInfoButton(wb_meta);
                });
                TabUIAPI.fetchVizPortal("getViewByPath", viewPath).then((view_meta) => {
                window.current_view_meta = view_meta;
              });
            } else {
              // If WB
            }
            window.current_wb_id = workbook_id;
          });

      }
      if (TabUI.context.currentDirectory.name == 'view-redirect'){


      }
      if (TabUI.context.currentDirectory.name == 'datasource'){
          let datasourceID = window.location.hash.replace("#/datasources/", "").split("/")[0]
          TabUIAPI.fetchVizPortal("getDatasourceById", datasourceID).then((ds_meta) => {
            console.log('Datasource meta', ds_meta);
            TabUIRender.renderDatasourceDownloadButton(ds_meta);
          });
      }
      if (TabUI.context.currentDirectory.name == 'recents'){


      }
      if (TabUI.context.currentDirectory.name == 'recommendations'){


      }
      if (TabUI.context.currentDirectory.name == 'shared'){


      }
      if (TabUI.context.currentDirectory.name == 'collections-my'){


      }
      if (TabUI.context.currentDirectory.name == 'collections-all'){


      }
      if (TabUI.context.currentDirectory.name == 'user'){

        TabUIRender.renderUserStatButton();

      }
      if (TabUI.context.currentDirectory.name != 'view'){

        TabUIRender.renderSidebarNews(TabUI.context.currentUserMeta);

      }

      
    };

    // UTILS ////////////////////////////

    this._elementReady = (selector) => {
      return new Promise((resolve, reject) => {
        let el = document.querySelector(selector);
        if (el) {
          resolve(el);
        }
        new MutationObserver((mutationRecords, observer) => {
          // Query for elements matching the specified selector
          Array.from(document.querySelectorAll(selector)).forEach((element) => {
            resolve(element);
            //Once we have resolved we don't need the observer anymore.
            observer.disconnect();
          });
        }).observe(document.documentElement, {
          childList: true,
          subtree: true,
        });
      });
    }

    this._mutationsEnded = () => {
      return new Promise((resolve, reject) => {
        let updatesOccur = true;
        const observer = new MutationObserver((mutations) => {
          updatesOccur = true;
        });
        observer.observe(window.document, {
          attributes: true,
          childList: true,
          characterData: true,
          subtree: true,
        });
        let mutationsCompletedCallback = () => {
          if (updatesOccur) {
            updatesOccur = false;
            setTimeout(mutationsCompletedCallback, 250);
          } else {
            observer.takeRecords();
            observer.disconnect();
            resolve("NO MORE MUTATIONS!");
          }
        };
        mutationsCompletedCallback();
      });
    }

    this.replaceUserLinks = (selector) => {
      $(selector).each(function () {
        owner_url = this.href.split("/");
        owner = owner_url[owner_url.length - 1];
        this.href = `https://staff.yandex-team.ru/${owner}`;
        this.setAttribute("target", "_blank");
        this.setAttribute("data-staff", owner);
      });
    }

    this.clearInnerHTML = (elementID) => {
      if (document.getElementById(elementID)) {
        document.getElementById(elementID).remove();
      }
    }

    this.getTagValue = (taglist, prefix) => {
      if (taglist.map((e) => e.includes(prefix)).includes(true)) {
        value = taglist
          .filter((tag) => tag.startsWith(prefix))[0]
          .replace(`${prefix}:`, "");
      } else {
        value = "";
      }
      return value;
    }

    // NDA/BUG ///////////////////////////////////////////

    this.renderNDA = () => {
      this.clearInnerHTML("TableauNDA");
      $("body").append(`<div id="TableauNDA">${TabUI.icons.nda_stamp}</div>`);
    };

    this.renderSupportButtons = () => {
      this._elementReady("body").then((someWidget) => {
        this.clearInnerHTML("TableauSupport");
        bug_html = `<div id="TableauSupport">
                            <div id="bug_handle" style="height: 10px; background-color: rgb(234, 234, 234); text-align: center; font-size:10px; line-height:10px; color:#aaa;">≡</div>
                            <div id="bug_btn" onclick="TabUIRender.btnBugClick()" title="Bug report" class="icon_container" style="border-bottom: 1px solid #ccc;">${TabUI.icons.bug}</div>
                            <div id="tg_btn" onclick="TabUIRender.btnChatClick()" title="Support chat" class="icon_container" style="">${TabUI.icons.telegram}</div>
                        </div>`;
        $("body").append(bug_html);
        $("div").drags({ handle: "#bug_handle", cursor: "move" });
      });
    }

    this.btnBugClick = () => {
      if (typeof current_wb_id !== "undefined") {
        wb_id = window.current_wb_id;
      } else {
        wb_id = "";
      }
      if (typeof TabUI.context.currentWorkbookMeta !== "undefined") {
        owner = TabUI.context.currentWorkbookMeta["owner"]["username"];
        wb_name = encodeURIComponent(TabUI.context.currentWorkbookMeta["name"]);
        unit = TabUI.context.currentWorkbookMeta["projects"][0]["name"];
        domain =
        TabUI.context.currentWorkbookMeta.projects.length > 1
            ? TabUI.context.currentWorkbookMeta["projects"][1]["name"]
            : "";
        path = TabUI.context.currentWorkbookMeta["projectPath"];
        meta = TabUI.context.currentWorkbookMeta;
        delete meta.datasources;
        wb_meta = JSON.stringify(meta);
      } else {
        owner = "";
        wb_name = "";
        unit = "";
        domain = "";
        path = "";
        wb_meta = "";
      }
      possible_projects = [
        "00 GO reports",
        "01 Taxi",
        "02 Eda",
        "03 Lavka",
        "04 Drive",
        "05 Delivery",
        "06 Scooter",
        "92 Support",
      ];
      if (!possible_projects.includes(unit)) {
        unit = "";
      }
      window.open(
        `https://forms.yandex-team.ru/surveys/78839/?tableau_workbook_id=${wb_id}&tableau_workbook_owner=${owner}&tableau_source_url=${window.location.hash.replace(
          "#",
          ""
        )}&tableau_wb_name=${wb_name}&tableau_wb_project=${unit}&tableau_wb_domain=${domain}&tableau_wb_path=${path}&tableau_message_from=${
          //window.current_user
          TabUI.context.currentUserMeta.username
        }&tableau_wb_meta=${wb_meta}`,
        "_blank" // <- This is what makes it open in a new window.
      );
    }

    this.btnChatClick = () => {
      window.open(
        `https://t.me/joinchat/WMgtWrE6dFwOLY_Z`,
        "_blank" // <- This is what makes it open in a new window.
      );
    }

    // Alerting ///////////////////////////////////////////

    this.renderAlerts = async (wb_id) => {
      let anchorSelector = `div.tb-main-content > div:first-child`
      let componentDivId = `tabui-alert`
      TabUIAPI.getWorkbookAlert(wb_id).then((data) => {
          if (!_.isEmpty(data)) {
            console.log("[TabUIRender.renderAlerts] — render:", data);
            // Cache the data to a variable
            alert_type = data[0]["type"];
            alert_message = data[0]["description"];
            alert_visibility = data[0]["visible_flg"];
            if (
              data[0]["startrack_issue_key"] == "" ||
              data[0]["startrack_issue_key"] == null
            ) {
              ticket_message = "";
            } else {
              alert_ticket = data[0]["startrack_issue_key"];
              ticket_message = `<br>See details in Tracker: <a target="_blank" href="https://st.yandex-team.ru/${alert_ticket}">${alert_ticket}</a>`;
            }
            message = alert_message + ticket_message;
            if (alert_visibility && document.getElementById(componentDivId) === null) {
              this._mutationsEnded().then((someWidget) => {
                console.log($('div.tb-main-content').html());
                this.clearInnerHTML(componentDivId);
                $(anchorSelector).after(
                    `<div id="${componentDivId}" style="padding:10px; text-align:center; background-color:${alert_bg(alert_type)};">
                      <div id="alert_close" onclick="TabUIRender.btnCloseAlertClick()" style="font-weight:bold; float:right; padding: 4px 4px 0 0; cursor: pointer;">✕</div>
                      ${message}
                    </div>`
                  ).show("slow");
              });
            } else {
              console.log(
                `Alert is not visible. Change visible_flg in snb_tableau.dm_tableau_announces_manual_act. Message: ${message}`
              );
            }
          } else {
            console.log(`No alerts was found`);
          }
        
          function alert_bg(type = "default") {
            let alertColors = {
              review: "#fffbe6",
              error: "#fbe8e6",
              default: "#f1f1f1",
              info: "#e1f1f5",
              }
            return alertColors.hasOwnProperty(type)
              ? alertColors[type]
              : alertColors["default"];
          }
        });
    }

    this.btnCloseAlertClick = () => {
      this.clearInnerHTML("tabui-alert");
    }

    // HOME PAGE ///////////////////////////////////////////

    this.renderPromotedWorkbooks = () => {

      var homePageConfig = [
        {
            title: "Taxi",
            logo: TabUI.icons.taxi_logo,
            promote_tag: "taxi",
        },
        {
            title: "Eda",
            logo: TabUI.icons.eda_logo,
            promote_tag: "eda",
        },
        {
            title: "Lavka",
            logo: TabUI.icons.lavka_logo,
            promote_tag: "lavka",
        },
        {
            title: "Delivery",
            logo: TabUI.icons.delivery_logo,
            promote_tag: "delivery",
        },
        ];

      
      if ($('[class*="WelcomeChannel_footer_"]')[0]) {
        home_selector = '[class*="Home_content-section_"]:first';
      } else {
        home_selector = '[class*="Home_root_"] > header';
      }
    
      this._elementReady('[class*="Home_content-section_"]').then((someWidget) => {
        this.clearInnerHTML("main_reports");
    
        // Rendering columns
        var columns = ``;
        homePageConfig.forEach((column) => {
          columns += `
                        <div class="flex-child">
                            <div style="display: flex; align-items: center;">
                                ${column.logo}
                                <span style="margin-left:10px; font-size: 16px;" class="CardView_action-row-name_fqcwmei">${column.title}</span>
                            </div>
                            <div id="${column.title}-reports" style="padding:0 0 0 5px;">
                              Loading ...
                            </div>
                        </div>`;
        });
        jQuery(home_selector).after(`
            <section class="Home_content-section_f6wkqso" id="main_reports" data-tb-test-id="main-reports">
                <header class="Channel_header_f1jel2fp"><h2>Main reports</h2></header>
                <div class="flex-container">
                    ${columns}
                </div>
            </section>`);
    
        // Fill columns with content
        
        TabUIAPI.getPromotedWorkbooks().then((promoted_workbooks) => {
    
          homePageConfig.map((column) => {  
            //workbooks = _.sortBy(_.where(promoted_workbooks, { promoted_column: column.promote_tag }), "sort_order");
            workbooks = _.sortBy(_.filter(promoted_workbooks, (wb) => {
            
              return wb.promoted_column == column.promote_tag 
            
            }), "sort_order");
            //console.log('Promored workbooks list: ', workbooks);
            var wb_list = ``;
            if (workbooks) {
              workbooks.forEach((workbook) => {
                wb_list += `<li style="margin-bottom:5px"><a href="/#/workbooks/${
                  workbook.workbook_id
                }" style="font-weight:bold;">${workbook.workbook_name}</a> — ${
                  workbook.workbook_description
                    ? workbook.workbook_description
                    : "No description"
                }</li>`;
              });
            }
            $(`#${column.title}-reports`).html(
              `<ul style="list-style-position: outside; padding-left:20px; list-style-type: '—  ';">${wb_list}</ul>`
            );
          });
        });
      });
    }

    this.renderSearchReports = () => {
      if ($('[class*="WelcomeChannel_footer_"]')[0]) {
        home_selector = '[class*="Home_content-section_"]:first';
      } else {
        home_selector = '[class*="Home_root_"] > header';
      }

      this._elementReady('[class*="Home_content-section_"]').then((someWidget) => {
        this.clearInnerHTML("tabui_searchReports");
    
        jQuery(home_selector).after(`
            <section class="Home_content-section_f6wkqso" id="main_reports" data-tb-test-id="main-reports">
                <header class="Channel_header_f1jel2fp"><h2>Search reports</h2></header>
                <div class="flex-container">
                    <iframe src="https://dwh-idm-integration.taxi.yandex-team.ru/static/start_page/index.html" style="width:100%; height:500px; border-bottom:1px solid #eee;" frameBorder="0">
                </div>
            </section>`);
    
      });

    }
    

    this.renderSignInErrors = () => {
      this._elementReady('.tb-login-title').then((someWidget) => {
        let errorDiv = document.getElementsByClassName('tb-error-box tb-error-no-site');
        let errorTitle = document.getElementsByClassName('tb-login-title');
        if (errorDiv && (errorTitle[0]?.innerText == 'Unable to Sign In')){
          console.log(`Error Content`);
          $('div.tb-error-box-message').html(`
          <!--div>🇷🇺 | Перейдите по <a style="color:blue;" href="https://dwh-idm-integration.taxi.yandex-team.ru/unsuspend-tableau-license/" target="_blank">ссылке</a> и потом заново зайдите в Табло</div>
          <div>🇬🇧 | Please open the <a style="color:blue;" href="https://dwh-idm-integration.taxi.yandex-team.ru/unsuspend-tableau-license/" target="_blank">link </a> and after that try to reach the server again.</div-->
          <div><iframe src="https://dwh-idm-integration.taxi.yandex-team.ru/unsuspend-tableau-license/" style="width:500px; height:400px; border:0px solid;"></iframe></div>
          `);
        }else{
          console.log(`No errors`);
        }
      });
    }

    // PROJECT PAGE ///////////////////////////////////////////

    this.renderWorkbooksCertifiedIcon = (workbooks) => {

      function _hasChild(element, tag) {
        for (var i = 0; i < element.children.length; i++) {
          if (element.children[i].tagName == tag) {
            return true;
          } else {
            return false;
          }
        }
      }

      let selector = '[data-tb-test-id*="name-"]';
      new MutationObserver((mutationRecords, observer) => {
        Array.from(document.querySelectorAll(selector)).forEach((element) => {
          jQuery(`${selector} > a`).each(function () {
            url = this.href.split("/");
            object_id = url[url.length - 1];
            object_type = url[url.length - 2];
            object_name = this.innerText;
            if (workbooks?.includes(object_id) && object_type == "workbooks") {
              //TAXIDWH-13795
              if (!_hasChild(this, "svg")) {
                this.insertAdjacentHTML(
                  "afterbegin",
                  `${TabUI.icons["certificate_s"]} `
                );
              }
            }
          });
        });
      }).observe(document.documentElement, {
        childList: true,
        subtree: true,
      });
    }

    this.renderSidebarNews = (userMeta) => {
      if(userMeta.news){
        /* Sidebar news add_news_module
          user_meta.news = 
              [{
                  "announce_creator": "pshevtsov",
                  "audience": [
                      "pshevtsov",
                      "shevtsoff"
                  ],
                  "created_at": "Mon, 29 Nov 2021 13:32:30 GMT",
                  "dt": "Mon, 29 Nov 2021 00:00:00 GMT",
                  "id": 1,
                  "link": "https://www.ya.ru",
                  "message": "Who's your daddy!?",
                  "message_type": "sidebar",
                  "subject": "Ypka!",
                  "updated_at": null,
                  "valid_from": "Mon, 29 Nov 2021 08:32:00 GMT",
                  "valid_to": "Wed, 29 Dec 2021 16:32:15 GMT"
              }]
          */
      
        let sidebar_news = _.filter(userMeta?.news, function (message) {
          return message.message_type == "sidebar";
        });
        let news = _.sortBy(sidebar_news, function (date) {
          return new Date(date.created_at);
        }).reverse();
        if (news.length !== 0) {
          console.log("GOOD NEWS EVERYONE!");
          //appending horizontal line
          //jQuery('[data-tb-test-id="nav-panel"] > ul').append('<li aria-disabled="true" aria-selected="false" data-itemvalue="" data-itemindex="5" tabindex="-1" style="outline: none;"><div class="Navigation_separator-expanded_f1agspuy"></div></li>');
      
          let news_containers = ``;
          news.forEach((item) => {
            d = new Date(item.created_at);
            newsdate = d.toLocaleDateString();
            news_containers += `
                          <div class="news_container" style="display: block; white-space: normal; font-size:10.5px; padding:0 0 15px 0;">
                              <div class="news_header" style="padding:0 0 5px 0;">
                                  <div class="news_date" style="float:right; display:inline; padding:2px 5px 10px 10px; font-size:10px;">${newsdate}</div>
                                  <div class="news_title" style="font-size:13px; ">${
                                    item.subject
                                  }</div>
                              </div>
                              <div class="news_content">${item.message}</div>
                              ${
                                item.link
                                  ? '<div align="right" class="news_seemore" style="padding:5px 0 0 0; font-size:12px"><a target="_blank" href="' +
                                    item.link +
                                    '">Read more...</a></div>'
                                  : ""
                              }
                          </div>`;
          });
      
          let news_module = `
                  <div id="TableauNews" style="max-width:220px;">
                  <li aria-disabled="true" aria-selected="false" data-itemvalue="" data-itemindex="5" tabindex="-1" style="outline: none; list-style: none;"><div class="Navigation_separator-expanded_f1agspuy"></div></li>
                  <div style="padding: 1px 24px 24px 24px;">
                      <div class="news_module_header" style="font-size: 14px; padding:0 0 10px 0">News</div>
                      <div id="news_body">
                          ${news_containers}
                      </div>
                  </div></div>`;
      
          this.clearInnerHTML("TableauNews");
          //appending news module
          jQuery('[data-tb-test-id="nav-panel"]').append(news_module);
        } else {
          console.log("[TabUIRender.renderSidebarNews] — There is no news");
        }
      }
    }

    this.renderToasts = (userMeta) => {
      if (userMeta.news){
          let toasts = _.filter(userMeta?.news, function (message) {
            toastTypes = ['toast','toast-info','toast-warning','toast-error','toast-success'];
            return toastTypes.includes(message.message_type);
          });
    
          toasts.forEach((toast) => {
            const toastType = {
              'toast' : false,
              'toast-info' : 'info',
              'toast-warning' : 'warning',
              'toast-error' : 'error',
              'toast-success' : 'success'
            };
            toastOpt = {
              heading: toast.subject,
              text: `${toast.message}<br><a href="${toast.link}">Read more...</a>`,
              hideAfter: false,
              position: 'bottom-right',
              ...(toastType[toast.message_type] != 'toast' && {icon: toastType[toast.message_type]}),
              beforeShow: function () {
              },
              afterShown: function () {
                TabUI.context.toasts.shown.push(toast.id)
                localStorage.setItem("TabUIToastShown", JSON.stringify(_.uniq(TabUI.context.toasts.shown)));          
              },
              afterHidden: function () {
                TabUI.context.toasts.hidden.push(toast.id)
                localStorage.setItem("TabUIToastHidden", JSON.stringify(_.uniq(TabUI.context.toasts.hidden)));
              }
            }
            if(!TabUI.context.toasts.hidden.includes(toast.id)){
              $.toast(toastOpt)
            }
          });
      }

    }

    // DATASOURCE PAGE //////////////////////////////////////////
    this.renderDatasourceDownloadButton = (dsData) => {

      //Datasource page embeddings
      console.log("Adding DS download button");
      this._elementReady('[data-tb-test-id="action-edit-datasource-Button"]').then((someWidget) => {
        if (!_.isEmpty(dsData)) {
          this.clearInnerHTML("download-button");
          url = window.location.origin + dsData["downloadUrl"] + "?noExtract=true";
          dsName = dsData["name"];
          $('[data-tb-test-id="action-edit-datasource-Button"]').after(
            `<a id="download-button" href="${url}" download="${dsName}">
              <button download="proposed_file_name" data-eventutils-optout="true" data-tb-test-id="-Button" tabindex="0" class="f1odzkbq low-density" style="font-weight: normal;">
                Download without extract
              </button>
            </a>`
          );
        }
      });
    }

    // WORKBOOK PAGE ////////////////////////////////////////////

    this.renderIDMButton = (wbData) => {
        //TAXIDWH-13796
        //Adding request personal access button
        this._elementReady(TabUI.selectors.page_title).then((someWidget) => {
          //$(document).on('DOMNodeInserted', function(e) {
          //    if ( $(e.target).hasClass('SpaceContainer_space-container_fuoy1tr') && isWorkbookPage ) {
          //clear_element("idm-personal");
          this.clearInnerHTML("idm_btn");
          console.log("Adding idm button");
          //jQuery(configHolder.ui.selectors.page_title).after(`<a id="idm-personal" target="_blank" title="Request personal access in IDM.\n Запросить персональный доступ к книге в IDM" href="${idm_path}" style="margin-top:5px;">${ui_icons["idm_s"]}</a>`);
          jQuery(TabUI.selectors.page_title).after(
            `<span id="idm_btn" style="cursor: pointer; margin-top:5px;">${TabUI.icons["idm_s"]}<span>`
          );
          console.log("Request access button added");
          tippy("#idm_btn", {
            content: "Loading...",
            theme: "light-border",
            delay: [0, 500],
            maxWidth: 650,
            interactive: true,
            placement: "bottom-start",
            trigger: "click",
            allowHTML: true,
            arrow: false,
            onShow(instance) {
              idm_path = `https://idm.yandex-team.ru/#rf-role=DaA5uHwb#taxi-dwh-idm-integration/tableau_analyst/tableau_personal_access/${wbData.id},rf-expanded=DaA5uHwb,rf=1`;
              idm_button = `<div align="right" style="padding:10px 0 5px 0;"><a href="${idm_path}" style="padding:5px 0 0 0;">
                      <button data-eventutils-optout="true" data-tb-test-id="-Button" tabindex="0" class="fppw03o low-density" style="cursor:pointer; font-weight: normal;">Request personal access</button></a></div>`;
              tipcontent = `<span style="font-weight:bold;">Permissions info:</span><br>
                      <div style="max-height: 300px; overflow-y: auto;"><table class="tippy-content" style="font-size:80%; font-weight:normal;" cellspacing="5">`;
              TabUIAPI.fetchIDM(
                "roles",
                `system=taxi-dwh-idm-integration&type=active&path=/role_approvers/node_approvers/tableau_analyst/tableau_personal_access/${wbData.id}/`
              )
                .then((approvers) => {
                  approverlist = "";
                  if (approvers.length !== 0) {
                    approvers = _.sortBy(approvers, "granted_at");
                    approvers.forEach((approver) => {
                      d = new Date(approver.granted_at);
                      grantdate = d.toLocaleDateString();
                      approverlist += `<li style="list-style-type: '— ';"><a href="https://staff.yandex-team.ru/${approver.user.username}" data-staff="${approver.user.username}">${approver.user.full_name}</a> <span title="Role granted">${grantdate}</span></li>`;
                    });
                  } else {
                    approverlist += `No approvers were found!`;
                  }
                  tipcontent += `
                      <tr style="vertical-align: baseline;">
                        <td style="padding:0 10px 0 0;">
                          <b>
                            <a target="_blank" href="https://idm.yandex-team.ru/reports/roles#f-is-expanded=true,f-status=active,f-system-type=all,f-role=taxi-dwh-idm-integration/role_approvers/node_approvers/tableau_analyst/tableau_personal_access/${wbData.id}">
                              Approvers
                            </a> (${approvers.length}) 
                          </b>
                        </td>
                        <td>
                        <div style="padding-bottom:5px;">
                          ${approverlist}
                        </div>
                        <a style="text-decoration: none; color: black; cursor:pointer;font-weight: normal; background-color: #eee; padding: 0px 3px; border:1px solid #ddd" onmouseover="this.style.backgroundColor='#ddd';" onmouseout="this.style.backgroundColor='#eee';" target="_blank" href="https://idm.yandex-team.ru/#rf-role=GOcWF10m#taxi-dwh-idm-integration/role_approvers/node_approvers/tableau_analyst/tableau_personal_access/${wbData.id},rf-expanded=GOcWF10m,rf=1">
                          Add approver
                        </a>
                        </td>
                      <tr>`;

                  return TabUIAPI.fetchIDM(
                    "roles",
                    `system=taxi-dwh-idm-integration&type=active&path=/tableau_analyst/tableau_personal_access/${wbData.id}/`
                  );
                })
                .then((personalaccess) => {
                  personallist = "";
                  if (personalaccess) {
                    personalaccess = _.sortBy(personalaccess, "granted_at").reverse();
                    personalaccess.forEach((person) => {
                      d = new Date(person.granted_at);
                      grantdate = d.toLocaleDateString();
                      personallist += `<li style="list-style-type: '— ';"><a href="https://staff.yandex-team.ru/${person.user.username}" data-staff="${person.user.username}">${person.user.full_name}</a> ${grantdate}</li>`;
                    });
                  } else {
                    personallist += `No approvers were found!`;
                  }

                  tipcontent += `
                      <tr style="vertical-align: baseline;">
                        <td style="padding:0 10px 0 0;">
                          <b>
                            <a target="_blank" href="https://idm.yandex-team.ru/reports/roles#f-is-expanded=true,f-status=active,f-system-type=all,f-role=taxi-dwh-idm-integration/tableau_analyst/tableau_personal_access/${wbData.id}">
                              Personal access
                            </a> (${personalaccess.length})
                          </b>                       
                        </td>
                        <td>
                          <div style="padding-bottom:5px;">
                          ${personallist}
                          </div>
                          <a style="text-decoration: none; color: black; cursor:pointer;font-weight: normal; background-color: #eee; padding: 0px 3px; border:1px solid #ddd" onmouseover="this.style.backgroundColor='#ddd';" onmouseout="this.style.backgroundColor='#eee';" target="_blank" href="https://idm.yandex-team.ru/#rf-role=DaA5uHwb#taxi-dwh-idm-integration/tableau_analyst/tableau_personal_access/${wbData.id},rf-expanded=DaA5uHwb,rf=1">
                          Request personal access
                          </a>
                        </td>
                      <tr>`;
                  tipcontent += `</table></div>`;
                  instance.setContent(tipcontent);
                });
            },
          });
          //    }
          //});
        });
    }

    this.renderDatalensButton = (wbData) => {
      this._elementReady(TabUI.selectors.page_title).then((someWidget) => {
        if (!_.isEmpty(wbData)) {
          let reportID = this.getTagValue(wbData["tags"], "datalens")
          if (reportID) {
            this.clearInnerHTML("datalens_btn");
            jQuery(TabUI.selectors.page_title).after(
              `<a id="datalens_btn" style="margin-top:5px;" title="Report in Datalens\n Отчёт в Даталенс" href="https://datalens.yandex-team.ru/${reportID}" target="_blank"><span style="cursor: pointer; margin-top:5px;">${TabUI.icons["datalens"]}<span></a>`
            );
          }
        }



      });      
    }

    this.renderTrackerButton = (wbData) => {
        //TAXIREPORTING-556
        let trackerQueues = 'TABL,TAXIREPORTING,TAXIANALYTICS,EXPOPS,TAXIWORLDANLT,EXPOPS'
        this._elementReady(TabUI.selectors.page_title).then((someWidget) => {
          this.clearInnerHTML("tracker_btn");
          jQuery(TabUI.selectors.page_title).after(
            `<span id="tracker_btn" style="cursor: pointer; margin-top:5px;">${TabUI.icons["tracker"]}<span>`
          );
          console.log("Tracker button added");
          tippy("#tracker_btn", {
            content: "Loading...",
            theme: "light-border",
            delay: [0, 500],
            maxWidth: 650,
            interactive: true,
            placement: "bottom-start",
            trigger: "click",
            allowHTML: true,
            arrow: false,
            onShow(instance) {
              TabUIAPI.fetchTracker(
                "issues",
                `filter=queue:${trackerQueues}&filter=reportID:${wbData.id}&order=key`
              ).then((trackerData) => {
                let tracker_table = `<span style="font-weight:bold;">Report tickets:</span><br>`;
                if (trackerData.length !== 0) {
                  tracker_table += `<div style="max-height: 300px; overflow-y: auto;"><table style="font-size:80%" cellspacing="5">
                              <tr><th>Ticket</th><th>Title</th><th>Author</th><th>Created</th></tr>`;
                  trackerData.forEach((ticket) => {
                    d = new Date(ticket.createdAt);
                    ticketCreated = d.toLocaleString();
                    tracker_table += `
                                  <tr>
                                  <td width="25%"><a target="_blank" href="https://st.yandex-team.ru/${
                                    ticket.key
                                  }" style="${
                      ticket.status.key == "closed"
                        ? "text-decoration: line-through;"
                        : ""
                    }">${ticket.key}</a></td>
                                  <td>${ticket.summary}</td>
                                  <td>${ticket.createdBy.display}</td>
                                  <td>${ticketCreated}</td>
                                  <tr>`;
                  });
                  tracker_table += `</table></div>`;
                } else {
                  tracker_table += `No tickets were found!`;
                }
                instance.setContent(tracker_table);
              });
            },
          });
        });
    }

    this.renderWorkbookID = (wbID) => {
      this._elementReady(TabUI.selectors.page_title).then((someWidget) => {
        this.clearInnerHTML("wb_id");
        $(TabUI.selectors.page_title).append(
          `<span id="wb_id"> (#${wbID})</span>`
        );
      });
    }

    this.renderWorkbookCertifiedIcon = (wbData) => {
      //Adding certified icon to view
      this._elementReady(TabUI.selectors.page_title).then((someWidget) => {
        this.clearInnerHTML("certified_report");
        if (!_.isEmpty(wbData)) {
          if (wbData["tags"].includes("certified:yes")) {
            jQuery(TabUI.selectors.page_title).before(
              `<a title="Report is certified\n Отчёт сертифицирован" id="certified_report" href="https://wiki.yandex-team.ru/taxi/analytics/tools/tableau/reports/certified/">${TabUI.icons["certificate_b"]}</a>`
            );
          }
        }
      });
    }

    this.renderDownloadButton = (wbData) => {
      console.log("Adding download button");
      this._elementReady('[data-tb-test-id="-Button"]').then((someWidget) => {
        if (!_.isEmpty(wbData)) {
          wb_owner = wbData["owner"]["username"];
          if (TabUI.context.currentUserMeta) {
            current_user_role = TabUI.context.currentUserMeta.siteRoleId;
            //if (wb_owner == current_user) {
            if (current_user_role == 10 || current_user_role == 11) {
              this.clearInnerHTML("download-button");
              url =
                window.location.origin + wbData["downloadUrl"] + "?noExtract=true";
              wb_name = wbData["name"];
              $('[data-tb-test-id="-Button"]').after(
                `<a id="download-button" href="${url}" download="${wb_name}"><button download="proposed_file_name" data-eventutils-optout="true" data-tb-test-id="-Button" tabindex="0" class="f1odzkbq low-density" style="font-weight: normal;">Download without extract</button></a>`
              );
            }
          }
        }
      });
    }

    this.renderWorkbookStatButton = (wbData) => {
      this._elementReady('[class*="SpaceContainer_space-masthead-area_"]').then((someWidget) => {
          this.clearInnerHTML("wb-dashboard-div");
          $('[class*="SpaceContainer_space-masthead-area_"]:first').after(
            `<div style="padding:10px; display: none;" id="wb-dashboard-div"><header class="Channel_header_f1jel2fp">
            <h2>Dashboard statistics</h2></header><div id="wb-dashboard-iframe"></div></div>`
          );
        }
      );
      this._elementReady(TabUI.selectors.page_title).then((someWidget) => {
        this.clearInnerHTML("wb-dashboard_button");
        jQuery(TabUI.selectors.page_title).after(
          `<div onclick="TabUIRender.btnWorkbookStatClick(${wbData.id})" id="wb-dashboard_button" title="Show dashboard statistics" style="cursor:pointer; margin-top:5px;">${TabUI.icons["stat"]}</div>`
        );
      });
    }

    this.btnWorkbookStatClick = (wbID) => {
      iframe = `<iframe src="https://tableau.taxi.yandex-team.ru/views/WorkbookStatsNEW/WorkbookDetailswide?&:iframeSizedToWindow=true&:embed=y&:showAppBanner=false&:display_count=no&:showVizHome=no&:toolbar=no&:tabs=no&wb_id=${wbID}" width="800px" height="400px" frameborder=0></iframe>`;
      $("#wb-dashboard-iframe").html(iframe);
      $("#wb-dashboard-div").slideToggle("slow", function () {
        // Animation complete.
      });
    }

    this.observeSidePanelClick = () => {
      $('[data-tb-test-id*="left-nav-Button"]').click(function () {
        if ($(this).attr("data-tb-test-id").includes("close")) {
          console.log("Panel minimized");
          $("#TableauNews").hide();
        } else if ($(this).attr("data-tb-test-id").includes("open")) {
          console.log("Panel shown");
          $("#TableauNews").show();
        }
      });
    }
    
    //============================= View page embeddings =========================================

    this.renderWikiEmbedButton = () => {
      this._elementReady('.PageHeader_viz-viewer-buttons_f1167hdv').then((someWidget) => {
        if (document.getElementsByClassName("PageHeader_viz-viewer-buttons_f1167hdv")) {
          //clear_embed_button();
          this.clearInnerHTML("wiki-embed");
          $('[data-tb-test-id="page-header-dataconnections-Button"]').after(
            `<button id="wiki-embed" data-eventutils-optout="true" data-tb-test-id="page-header-embed-Button" onclick="TabUIRender.btnWikiEmbedClick()" title="Embed this view in wiki" class="f1odzkbq fyvorft low-density" style="cursor: pointer;" tabindex="0"><span class="PageHeader_text-button_f1xsrgrx">${TabUI.icons["embeding"]}<span id="wiki-embed-text">Embed in Wiki</span></span></button>`
          );
          console.log("Embed button added");
        }
      });
    }

    this.btnWikiEmbedClick = () => {
      let viewPath = TabUI.context.currentDirectory.id + '/' + TabUI.context.currentDirectory.subDirectory
      var copyText = `{{iframe src="${window.location.origin}/views/${viewPath}?&:iframeSizedToWindow=true&:embed=y&:showAppBanner=false&:display_count=no&:showVizHome=no&:toolbar=no&:tabs=no" width="1400px" height="900px" frameborder=0}}`;
      var dummy = document.createElement("textarea");
      document.body.appendChild(dummy);
      dummy.value = copyText;
      dummy.select();
      dummy.setSelectionRange(0, 99999); /* For mobile devices */
      document.execCommand("copy");
      document.body.removeChild(dummy);
      alert(
        `Embedding code for wiki was successfully copied to clipboard: \n ${copyText}`
      );
    }

    this.renderViewCertifiedIcon = (wbData) => {
      if (!TabUIAPI._hasError(wbData)) {
        console.log("Trying to add Certified icon");
        this._elementReady('[data-tb-test-id*="breadcrumb-workbook-"]').then((someWidget) => {
            if (wbData["tags"].includes("certified:yes")) {
              this.clearInnerHTML("wb_certified");
              jQuery('[data-tb-test-id*="breadcrumb-workbook-"] > a').prepend(
                `${TabUI.icons["certificate_s"]} `
              );
            }
          }
        );
      }
    }

    this.renderSubtitle = (wbData) => {

      function staff_card_add() {
        var users = document.querySelectorAll("[data-staff]");
        users.forEach(function (user) {
          new StaffCard(user, user.dataset.staff);
        });
      }

      if (!TabUIAPI._hasError(wbData)) {
        if (wbData.datasourcesLastRefresh) {
          lastDataRefresh = wbData.datasourcesLastRefresh;
        } else {
          d = new Date(wbData.updatedAt);
          lastDataRefresh = d.toLocaleString();
        }
    
        this._elementReady('[data-tb-test-id="breadcrumb-list"]').then((someWidget) => {
          this.clearInnerHTML("wb_subtitle");
          if (!document.getElementById("wb_subtitle")) {
            let subtitle = `<div id="wb_subtitle" style="display:block; color:#ccc; font-size:90%">
                    Contact owner: <a target="_blank" href="https://staff.yandex-team.ru/${wbData.owner.username}" data-staff="${wbData.owner.username}"><b>${wbData.owner.displayName}</b></a> 
                    | 
                    Last data refresh: <a target="_blank" href="https://tableau.taxi.yandex-team.ru/#/workbooks/${wbData.id}/datasources" id="subtitle_date"><b>${lastDataRefresh}</b></a></div>`;
            jQuery('[class*="Breadcrumbs_container_"]:first').after(subtitle);
            jQuery('[class*="Breadcrumbs_container_"]').css({"line-height": "32px", "height": "24px"});
            tippy("#subtitle_date", {
              content: "Loading...",
              theme: "light-border",
              maxWidth: 650,
              interactive: true,
              placement: "bottom-start",
              allowHTML: true,
              //arrow: false,
              onShow(instance) {
                TabUIAPI.fetchVizPortal("getDatasources", wbData.id).then((ds) => {
                  let datasources = ds.datasources;
                  let ds_table = `<span style="font-weight:bold;">Report datasources:</span><br>`;
                  ds_table += `<table class="tippy-content" style="font-size:80%;" cellspacing="5">
                                    <tr><th>Datasource</th><th>Connects to</th><th width="10%">Data is</th><th width="15%">Update Time</th></tr>`;
                  datasources.forEach((ds, index) => {
                    if (ds.hasExtracts) {
                      ds_refresh = new Date(
                        ds.connectionDetails.lastRefreshedAt || ds.lastRefreshedAt
                      ).toLocaleString();
                      wbData.datasourcesLastRefresh = ds_refresh;
                    } else {
                      if (
                        ds.connectionDetails.lastRefreshedAt ||
                        ds.lastRefreshedAt
                      ) {
                        ds_refresh = new Date(
                          ds.connectionDetails.lastRefreshedAt || ds.lastRefreshedAt
                        ).toLocaleString();
                      } else {
                        ds_refresh = " ";
                      }
                    }
                    ds_table += `<tr>
                                    <td>${ds.name}</td>
                                    <td title='${JSON.stringify(
                                      ds.connectionDetails,
                                      null,
                                      2
                                    )}'>${
                      ds.connectionDetails.type == "tableauserver"
                        ? "Published Datasource"
                        : ds.connectionDetails.serverName
                    }</td>
                                    <td>${ds.hasExtracts ? "Extract" : "Live"}</td>
                                    <td>${ds_refresh}</td>
                                    </tr>`;
                  });
                  ds_table += `</table>`;
                  instance.setContent(ds_table);
                });
              },
            });
            staff_card_add();
          }
        });
      }
    }

    this.renderViewWorkbookID = (wbData) => {
      if (!TabUIAPI._hasError(wbData)) {
        console.log("[TabUIRender.renderViewWorkbookID] — data:", wbData);
        this._elementReady('[data-tb-test-id*="breadcrumb-workbook-"]').then(
          (someWidget) => {
            this.clearInnerHTML("wb_id");
            if (!document.getElementById("wb_id")) {
              jQuery('[data-tb-test-id*="breadcrumb-workbook-"] > a').append(
                `<span id="wb_id"> (#${wbData.id})</span>`
              );
            }
          }
        );
      }
    }

    this.renderWorkbookInfoButton = (wbData) => {

      function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
      }

      if (!TabUIAPI._hasError(wbData)) {
        console.log("[TabUIRender.renderWorkbookInfoButton] — data:", wbData);
        this._elementReady(TabUI.selectors.viewpage_favorite_button).then(
          (someWidget) => {
            this.clearInnerHTML("info_btn");
            if (!document.getElementById("info_btn")) {
              jQuery(TabUI.selectors.viewpage_favorite_button).before(
                `<span id="info_btn" style="cursor: pointer; margin:4px 5px 0 5px;">${TabUI.icons["info"]}<span>`
              );
              tippy("#info_btn", {
                content: "Loading...",
                theme: "light-border",
                trigger: "click",
                hideOnClick: true,
                delay: [0, 500],
                maxWidth: 650,
                interactive: true,
                placement: "bottom-start",
                allowHTML: true,
                arrow: false,
                onShow(instance) {
                  let data = [
                    {
                      title: "Description",
                      value: wbData.description.replace(/\n/g, "<br />"),
                    },
                    {
                      title: "Report Type",
                      value: capitalizeFirstLetter(
                        TabUIRender.getTagValue(wbData["tags"], "report_type")
                      ),
                    },
                    {
                      title: "Security level",
                      value: capitalizeFirstLetter(
                        TabUIRender.getTagValue(wbData["tags"], "sec_level")
                      ),
                    },
                    {
                      title: "Review ticket",
                      value: TabUIRender.getTagValue(wbData["tags"], "review_ticket")
                        ? `<a href="https://st.yandex-team.ru/${TabUIRender.getTagValue(wbData["tags"], "review_ticket")}">${TabUIRender.getTagValue(wbData["tags"], "review_ticket")}</a>`
                        : "",
                    },
                  ];
                  let tipcontent = `<span style="font-weight:bold;">Report details:</span><br>
                            <div style="max-height: 300px; overflow-y: auto;"><table class="tippy-content" style="font-size:80%; font-weight:normal;" cellspacing="5">`;
                  data.forEach((row, index) => {
                    if (row.value) {
                      tipcontent += `<tr style="vertical-align: baseline;"><td><b>${row.title}</b></td><td>${row.value}</td><tr>`;
                    }
                  });
                  tipcontent += `</table></div>`;
                  instance.setContent(tipcontent);
                },
                onClickOutside(instance, event) {
                  instance.hide();
                },
              });
            }
          }
        );
      }
    }

    //============================= User page embedings ============================================

    this.renderUserStatButton = () => {
      console.log("Adding dash for user");
      this._elementReady('[class*="SpaceContainer_space-masthead-area_"]').then(
        (someWidget) => {
          this.clearInnerHTML("user-dashboard-iframe");
          $('[class*="SpaceContainer_space-masthead-area_"]:first').after(
            `<div style="padding:10px; display: none;" id="user-dashboard-iframe"><header class="Channel_header_f1jel2fp"><h2>User statistics</h2></header><iframe src="https://tableau.taxi.yandex-team.ru/views/Userwidget/TableauUserInfowide?&amp;:iframeSizedToWindow=true&amp;:embed=y&amp;:showAppBanner=false&amp;:display_count=no&amp;:showVizHome=no&amp;:toolbar=no&amp;:tabs=no&amp;login=${
              window.location.hash.split("?")[0].split("/")[3]
            }" height="400px" width="800px" frameborder="0"></iframe></div>`
          );
        }
      );
      this._elementReady(TabUI.selectors.page_title).then((someWidget) => {
        this.clearInnerHTML("user-dashboard_button");
        jQuery(TabUI.selectors.page_title).after(
          `<div onclick="TabUIRender.btnUserStatClick()" id="user-dashboard_button" title="Show user stat" style="cursor:pointer; margin-top:5px;">${TabUI.icons["stat"]}</div>`
        );
      });
    }

    this.btnUserStatClick = () => {
      $("#user-dashboard-iframe").slideToggle("slow", function () {
        // Animation complete.
      });
    }

    this.renderUsersLicenses = async () => {

      let creators = await TabUIAPI.fetchVizPortal('getUsersByRoleName', 'Creator');



    }

    //============================= Error page embeddings =========================================
    this.renderErrorPage = (wbData) => {
      if (_.isEmpty(wbData)) {
          console.log("[TabUIRender.renderErrorPage] — render: workbook doesn't exist");
          wb_id = null
          owner = null
      } else {
          console.log("[TabUIRender.renderErrorPage] — render: workbook exists");
          wb_id = wbData.workbook_id
          owner = wbData.workbook_owner
      }
        //{"workbook_id":8559,"workbook_luid":"06e3fb14-d29b-48ce-a5e5-c2a68d41fbc2","workbook_name":"Postcards Events","workbook_owner":"natalyazorina"}

      //TAXIDWH-13753: [Custom JS] Русский текст для сообщений об ошибках
      error_msg = {
        no_access: {
          title: {
            en: `You don't have necessary permissions for workbook: ${wbData?.workbook_name}`,
            ru: `У вас нет необходимых прав для просмотра книги ${wbData?.workbook_name}`,
          },
          description: {
            en: `Please request personal access in IDM or ask workbook owner for a help: <a target="_blank" href="https://staff.yandex-team.ru/${owner}" data-staff="${owner}">${owner}</a>`,
            ru: `Можете запросить доступ к книге через IDM или обратиться к разарботчику книги за помощью: <a target="_blank" href="https://staff.yandex-team.ru/${owner}" data-staff="${owner}">${owner}</a>`,
          },
          btn: {
            en: "Request Access in IDM",
            ru: "Запросить доступ в IDM",
          },
          btn_style: `background: #ffde40;`,
          url: `https://idm.yandex-team.ru/#rf-role=KhPnbgmk#taxi-dwh-idm-integration/tableau_analyst/tableau_personal_access/${
            wb_id ? wb_id : ""
          },rf-expanded=KhPnbgmk,rf=1`,
        },
        no_workbook: {
          title: {
            en: "Workbook doesn't exist",
            ru: "Книга не существует",
          },
          description: {
            en: `It seems like workbbok has been deleted from the server. You can use <a href="https://tableau.taxi.yandex-team.ru/#/search/views" style="text-decoration:underline;">🔍 search capabilities</a> to find needed infromation`,
            ru: `Кажется книга была удалена с сервера. Воспользуйтесь <a href="https://tableau.taxi.yandex-team.ru/#/search/views" style="text-decoration:underline;">поиском</a>, чтобы найти её текущую версию`,
          },
          btn: {
            en: "Back to All Views",
            ru: "Перейти к списку книг",
          },
          btn_style: ``,
          url: `https://tableau.taxi.yandex-team.ru/#/views`,
        },
      };
      if (document.getElementById("error-content")) {
        console.log(
          `Error Content. Rendering message for workbook ${wb_id} with type ${typeof wb_id}`
        );
        //Проверяем, что есть див с id=error-content и он содержит That page could not be accessed
        if (
          $("#error-content").length &&
          $("#error-content > div > div > div:nth-child(1)")[0].innerText ==
            "That page could not be accessed."
        ) {
          flow = _.isNull(wb_id) ? "no_workbook" : "no_access";
          console.log(
            `There is an element #error-content and page title "That page could not be accessed." \nWorkflow: ${flow}`
          );
          msg_content = `
                    <div id="error-msg">
                        <div role="alert" aria-atomic="true">
                            <div class="tb-error-box-message-first">
                                ${error_msg[flow].title.en}<br>
                                <span style="font-size:70%; color:rgba(0,0,0,0.5);">${error_msg[flow].title.ru}</span>
                            </div>
                            <div class="tb-error-box-message-second">
                                ${error_msg[flow].description.en}<br>
                                <span style="font-size:80%; color:rgba(0,0,0,0.5);">${error_msg[flow].description.ru}</span>
                            </div>
                        </div>
                        <br>
                        <!--a style="width: 115px; height: 25px; background: #ffde40; padding: 10px; text-align: center; border-radius: 5px; color: black; font-weight: bold; line-height: 25px;" href="${error_msg[flow].url}">${error_msg[flow].btn.en}</a-->
                        <a href="${error_msg[flow].url}" style="">
                            <button data-eventutils-optout="true" data-tb-test-id="-Button" tabindex="0" class="fppw03o low-density" style="cursor:pointer; font-weight: normal; ${error_msg[flow].btn_style}">${error_msg[flow].btn.en}</button>
                            </a>
                        <br>
                        <div style="font-size:80%; color:rgba(0,0,0,0.5); padding:5px; ">${error_msg[flow].btn.ru}</div>
                    </div>`;
          $(".tb-error-box").html(msg_content);
        }
      }
    }

  }


  var setCSS = (css_text) => {
    TabUIRender.clearInnerHTML("tabui-css");
    style = document.createElement("style");
    style.id = "tabui-css";
    style.innerHTML = css_text;
    document.head.appendChild(style);
    console.log('[setCSS] — new styles applyed');
  }

  var setLogging = () => {
    originalLog = console.log;
    // Overwriting
    console.log = function () {
      if(TabUI.logging){
        var args = [].slice.call(arguments);
        originalLog.apply(console.log, [getCurrentDateString()].concat(args));
      }
    };
    // Returns current timestamp
    function getCurrentDateString() {
      return new Date().toISOString() + " ::";
    }
  }

  // expose TabUI to the global object
  window.TabUI = TabUI;
  window.TabUIAPI = TabUIAPI;
  window.TabUIRender = TabUIRender;
  window.TablUILocator = TablUILocator;
  setCSS(TabUI.css);
  setLogging();
  TabUIMeta.setCertifiedWorkbooks();
  TabUIMeta.setCurrentUser();

  //Set Context Meta
  TabUI.context.currentDirectory.name = TablUILocator().currentDir;
  TabUI.context.currentDirectory.id = TablUILocator().hashParts?.id;
  TabUI.context.currentDirectory.subDirectory = TablUILocator().hashParts?.subDirectory;
  console.log('TabUI:', TabUI);

  //Initial render
  TabUIRender.renderPage();
  TabUIRender.renderToasts(TabUI.context.currentUserMeta);

  // HASHCHANGE ////////////////////////////////////////////////////////////////////////////////////////////////////////
  window.addEventListener('hashchange', (event) => {  
    TabUI.context.currentDirectory.name = TablUILocator({oldUrl: event.oldURL, newUrl: event.newURL}).currentDir;
    TabUI.context.currentDirectory.id = TablUILocator({oldUrl: event.oldURL, newUrl: event.newURL}).hashParts?.id;
    TabUI.context.currentDirectory.subDirectory = TablUILocator({oldUrl: event.oldURL, newUrl: event.newURL}).hashParts?.subDirectory;
    
    //Render on every hashchange
    TabUIRender.renderPage();
  });

  // MOUSEDOWN ////////////////////////////////////////////////////////////////////////////////////////////////////////
  document.addEventListener('mousedown', (event) => {  
    
    TabUIRender.renderWorkbooksCertifiedIcon(TabUI.context.certifiedWorkbooks);

  });

  // MOUSEOVER ////////////////////////////////////////////////////////////////////////////////////////////////////////
  document.addEventListener("mouseover", function (e) {
    //Auto adding Staff card to links
    TabUIRender.replaceUserLinks(TabUI.selectors.datagrid_project_owner);
    TabUIRender.replaceUserLinks(TabUI.selectors.datagrid_workbook_owner);
    TabUIRender.replaceUserLinks(TabUI.selectors.datagrid_view_owner);
    TabUIRender.replaceUserLinks(TabUI.selectors.page_header_owner);

    var el = e.target;
    if (!el.matches("[data-staff]")) {
      return;
    }

    var inited = el.dataset.staffInited;
    if (!inited) {
      var login = el.dataset.staff;
      var card = new StaffCard(el, login);
      card.onHover();
      el.dataset.staffInited = true;
    }
  });


}) (typeof window !== 'undefined' ? window : null, typeof  window !== 'undefined' ? document : null);