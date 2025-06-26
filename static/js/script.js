document.addEventListener("DOMContentLoaded", function () {
  /* Section about arrow in th eleft corner of navbar and sidebar that is meant to appear after clicking
the arrow icon

*/
  const arrow = document.querySelector(".navbar .arrow");
  const sidebar = document.querySelector(".navbar .sidebar");

  arrow.addEventListener("click", function () {
    arrow.classList.toggle("action");
    sidebar.classList.toggle("action");
  });

  /* Section about go-back button functionality, it's meant to redirect user to the previous page in certain 
  situations, it uses method match() to check proper ids and send user to the correct page. 

  */

  if (document.getElementById("go-back")) {
    document.getElementById("go-back").addEventListener("click", function () {
      const referrer = document.referrer;

      const forbiddenTemplates = [];

      const url = new URL(referrer);

      const path = url.pathname;

      console.log("Ref: ", referrer);
      console.log("Path:", path);

      // debugger;

      // let checkPreviousPageGroupTask = forbiddenTemplatesGroupTask.some(page => referrer.includes(page))

      if (
        referrer.includes("group-update") ||
        referrer.includes("group-task-create") ||
        referrer.includes("group-task-delete") ||
        referrer.includes("group-member-delete")
      ) {
        window.location.href = "/groups/";
      } else if (referrer.includes("group-task-update")) {
        if (path) {
          const match = path.match(
            /\/group\/(\d+)\/group-task-update\/(\d+)\/?/
          );
          pk = null;

          if (match) {
            pk = match[1];
          }

          if (pk) {
            window.location.href = `/group/${pk}`;
          } else {
            window.history.back();
          }
        } else {
          console.error("Path is not defined");
        }
      }
      // there was also code for group-task-delete, now nvm
      else if (referrer.includes("invites")) {
        const match = path.match(/\/groups\/invites\/(\d+)\/?/);

        if (match) {
          window.location.href = "/groups/";
        } else {
          window.history.back();
        }
      } else {
        window.history.back();
      }
    });
  }

  /* Section about adding new participants to a group, 
    it checks the value of input where leader of the group writes usernames of users that the leader wants to add to the group,
    another version if I decided to make the choice of the user always visible

  */
  const searchParticipants = document.getElementById("search-participants");

  if (searchParticipants) {
    searchParticipants.addEventListener("keyup", () => {
      const searchQuery = searchParticipants.value.toLowerCase();

      const participants = [
        ...document.querySelectorAll("#id_participants div"),
      ];

      const participantList = document.querySelector("#id_participants");

      if (searchQuery == "") {
        participantList.classList.remove("action");
      } else {
        participantList.classList.add("action");
      }

      participants.forEach((user) => {
        const username = user.textContent.toLowerCase();

        if (username.includes(searchQuery)) {
          user.style.display = "";
        } else {
          user.style.display = "none";
        }
      });
    });
  }

  /* Section about finding proper line about uploading files in the group-task-form and showing name of the
   file chosen by the user,


  */

  if (document.getElementById("file1")) {
    const file = document.getElementById("file1");
    file.addEventListener("change", function () {
      const fileTitle = file.files[0].name;
      document.getElementById("filename1").textContent =
        "Selected file: " + fileTitle;
    });
  }

  if (document.getElementById("file2")) {
    const file = document.getElementById("file2");
    file.addEventListener("change", function () {
      const fileTitle = file.files[0].name;
      document.getElementById("filename2").textContent =
        "Selected file: " + fileTitle;
    });
  }

  if (document.getElementById("file3")) {
    const file = document.getElementById("file3");
    file.addEventListener("change", function () {
      const fileTitle = file.files[0].name;
      document.getElementById("filename3").textContent =
        "Selected file: " + fileTitle;
    });
  }

  /* Section about interactive search of task in the Dashboard, DailyTasksPage adn GroupDetailPage


  */

  const searchTasks = document.getElementById("search-tasks");

  if (searchTasks) {
    searchTasks.addEventListener("keyup", () => {
      const searchQueryTasks = searchTasks.value.toLowerCase();

      const allTasksWrapper = [
        ...document.querySelectorAll(".task-items-wrapper .task-wrapper"),
      ];

      allTasksWrapper.forEach((task) => {
        const title = task
          .querySelector(".task-info h3")
          .textContent.toLowerCase();
        const infoAll = [...task.querySelectorAll(".task-info h5")];

        if (infoAll.length) {
          for (let i = 0; i < infoAll.length; i++) {
            if (
              infoAll[i].textContent.toLowerCase().includes(searchQueryTasks) ||
              title.includes(searchQueryTasks)
            ) {
              task.style.display = "";
              break;
            } else {
              task.style.display = "none";
            }
          }
        } else {
          if (title.includes(searchQueryTasks)) {
            task.style.display = "";
          } else {
            task.style.display = "none";
          }
        }
      });
    });
  }

  /* Section about interactive search of Notifications on NotificationListPage


  */

  const searchNotifications = document.getElementById("search-notifications");

  if (searchNotifications) {
    searchNotifications.addEventListener("keyup", () => {
      const searchQueryNotifications = searchNotifications.value.toLowerCase();

      const allNotificationsWrapper = [
        ...document.querySelectorAll(
          ".notifications-items-wrapper .notification-wrapper"
        ),
      ];

      allNotificationsWrapper.forEach((item) => {
        const title = item
          .querySelector(".notification-info h3")
          .textContent.toLowerCase();

        if (title.includes(searchQueryNotifications)) {
          item.style.display = "";
        } else {
          item.style.display = "none";
        }
      });
    });
  }

  /* Section about displaying list of changes in a GroupTask notification, it happens by using one <h4> element on a page and processing its value into seperate <li> elements


  */

  const changesList = document.querySelector(".list-of-changes");
  const changesString = document.querySelector(
    ".list-of-changes .changes-holder"
  );
  let changesTable = [];

  if (changesList && changesString) {
    if (changesString !== "") {
      // console.log(changesString);
      changesTable = changesString.textContent.split(", ");
      changesTable.shift();
      console.log(changesTable);
      changesTable.forEach((item) => {
        let new_item = document.createElement("li");
        new_item.textContent = item;
        changesList.appendChild(new_item);
      });
    }
    changesString.style.display = "none";
  }

  /* Section about 'check all' checkbox in the Notifications and History of each GroupTask,
  making it so all the other checkboxes on a page are checked or unchecked,
  also to make a button 'Delete All' appear whenever any checkbox is checked


  */

  const checkAllBox = document.querySelector(".notification-checkbox-all");
  const checkList = [...document.querySelectorAll(".notification-checkbox")];
  const deleteAllBtn = document.querySelector(".button.delete-checkbox");
  let checkedFlag = false;

  if (checkAllBox) {
    console.log(checkAllBox);

    checkAllBox.addEventListener("click", (e) => {
      if (e.target.checked === true) {
        deleteAllBtn.classList.remove("hidden");
      } else {
        deleteAllBtn.classList.add("hidden");
      }
      if (checkList) {
        checkList.forEach((item) => {
          console.log(item.checked);
          if (e.target.checked === true) {
            item.checked = true;
          } else {
            item.checked = false;
          }
        });
      }
    });
  }

  if (checkList) {
    checkList.forEach((item) => {
      item.addEventListener("change", () => {
        for (let i = 0; i < checkList.length; i++) {
          if (checkList[i].checked === true) {
            checkedFlag = true;
            break;
          } else {
            checkedFlag = false;
          }
        }
        if (checkedFlag) {
          deleteAllBtn.classList.remove("hidden");
        } else {
          deleteAllBtn.classList.add("hidden");
        }
      });
    });
  }

  /* Section about interactive filtering group tasks specifically in terms of their statuses


  */

  const selectTasks = document.getElementById("group-task-filter");
  const checkedGroupTasks = [
    ...document.querySelectorAll(".task-wrapper.group"),
  ];
  // console.log(selectTasks);

  if (selectTasks) {
    selectTasks.addEventListener("change", (e) => {
      checkedGroupTasks.forEach((task) => {
        let taskText = task.querySelector(
          ".group-task-members.status h4"
        ).textContent;
        taskText = taskText.slice(13, taskText.length);
        if (e.target.value === "all") {
          task.style.display = "";
        } else if (e.target.value === taskText) {
          task.style.display = "";
        } else {
          task.style.display = "none";
        }
      });
    });
  }

  /* Section about interactive searching groups' and their leaders' names on the group list page


  */

  const searchMyGroups = document.getElementById("search-my-groups");

  if (searchMyGroups) {
    searchMyGroups.addEventListener("keyup", () => {
      const searchQueryGroups = searchMyGroups.value.toLowerCase();

      const allGroupsWrapper = [
        ...document.querySelectorAll(".group-list .group-wrapper"),
      ];

      allGroupsWrapper.forEach((group) => {
        const groupName = group
          .querySelector(".group-title h3 a")
          .textContent.toLowerCase();
        const leaderName = group
          .querySelector(".group-title h2 a")
          .textContent.toLowerCase();

        if (groupName.includes(searchQueryGroups)) {
          group.style.display = "";
        } else if (leaderName.includes(searchQueryGroups)) {
          group.style.display = "";
        } else {
          group.style.display = "none";
        }
      });
    });
  }

  /* Section about adding classes to certain div elements while displaying GroupTask() instances,
    it helps with creating additional borders for displayed text inside task-wrapper element


  */

  if (checkedGroupTasks) {
    checkedGroupTasks.forEach((task) => {
      let taskStatus = task.querySelector(
        ".group-task-members.status h4"
      ).textContent;
      taskStatus = taskStatus.slice(13, taskStatus.length);
      const taskContainer = task.querySelector(".task-title.group");
      if (taskStatus === "need adjustments") {
        taskContainer.classList.add("need-adjustments");
      } else {
        taskContainer.classList.add(taskStatus);
      }
    });
  }

  /* Section related to the dashboard and 4 buttons on the page, each one related to one type of tasks,


  there has to be addeda button for group tasks,

  also there was an idea to make it so the user's choice about which list to display, would be remembered while using the application, in the end I commented it


  */

  const completedTasksBtn = document.querySelector(".tasks-counter.completed");
  const allTasksBtn = document.querySelector(".tasks-counter.all");
  const overdueTasksBtn = document.querySelector(".tasks-counter.overdue");
  const pendingTasksBtn = document.querySelector(".tasks-counter.pending");
  const groupTasksBtn = document.querySelector(".tasks-counter.group");

  const completedTasks = document.querySelector(
    ".task-items-wrapper.completed"
  );
  const allTasks = document.querySelector(".task-items-wrapper.all");
  const overdueTasks = document.querySelector(".task-items-wrapper.overdue");
  const pendingTasks = document.querySelector(".task-items-wrapper.pending");
  const groupTasks = document.querySelector(".task-items-wrapper.group");

  let allTasksFlag = true;
  let completedTasksFlag = false;
  let overdueTasksFlag = false;
  let pendingTasksFlag = false;
  let groupTasksFlag = true;

  const updateTaskList = function () {
    if (allTasksFlag) {
      allTasks.classList.add("action");
      groupTasks.classList.add("action");
    } else {
      allTasks.classList.remove("action");
    }

    if (completedTasksFlag) {
      completedTasks.classList.add("action");
      groupTasks.classList.remove("action");
    } else {
      completedTasks.classList.remove("action");
    }

    if (overdueTasksFlag) {
      overdueTasks.classList.add("action");
      groupTasks.classList.remove("action");
    } else {
      overdueTasks.classList.remove("action");
    }

    if (pendingTasksFlag) {
      pendingTasks.classList.add("action");
      groupTasks.classList.remove("action");
    } else {
      pendingTasks.classList.remove("action");
    }

    if (groupTasksFlag) {
      groupTasks.classList.add("action");
    }
  };

  if (allTasksBtn) {
    updateTaskList();
  }

  if (allTasksBtn) {
    allTasksBtn.addEventListener("click", function () {
      allTasksFlag = true;
      completedTasksFlag = false;
      overdueTasksFlag = false;
      pendingTasksFlag = false;
      groupTasksFlag = false;
      updateTaskList();
      //   updateFlags();
    });
  }

  if (completedTasksBtn) {
    completedTasksBtn.addEventListener("click", function () {
      allTasksFlag = false;
      completedTasksFlag = true;
      overdueTasksFlag = false;
      pendingTasksFlag = false;
      groupTasksFlag = false;
      updateTaskList();
      //   updateFlags();
    });
  }

  if (overdueTasksBtn) {
    overdueTasksBtn.addEventListener("click", function () {
      allTasksFlag = false;
      completedTasksFlag = false;
      overdueTasksFlag = true;
      pendingTasksFlag = false;
      groupTasksFlag = false;
      updateTaskList();
      //   updateFlags();
    });
  }

  if (pendingTasksBtn) {
    pendingTasksBtn.addEventListener("click", function () {
      allTasksFlag = false;
      completedTasksFlag = false;
      overdueTasksFlag = false;
      pendingTasksFlag = true;
      groupTasksFlag = false;
      updateTaskList();
      //   updateFlags();
    });

    if (groupTasksBtn) {
      groupTasksBtn.addEventListener("click", function () {
        allTasksFlag = false;
        completedTasksFlag = false;
        overdueTasksFlag = false;
        pendingTasksFlag = false;
        groupTasksFlag = true;
        updateTaskList();
        //   updateFlags();
      });
    }
  }
});

/* Section about the bell icon in the navbar and a place for notifications to appear 
      not relevant atm
    */

// const bell = document.querySelector(".bell");
// const notificationsBar = document.querySelector(".navbar .notifications");

// bell.addEventListener("click", function () {
//   // bell.classList.toggle("action")
//   notificationsBar.classList.toggle("action");
// });
