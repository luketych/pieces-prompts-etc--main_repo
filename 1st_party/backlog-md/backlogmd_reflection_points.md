# Mid-Task Reflection Guide

When working from `backlog.md` and actively implementing a task, take a moment to pause and reflect on your current development context. You should pause and determine if it is a good opportunity to reflect during the following example conditions:

- claude has completed one of its tasks, ie after each of these internal Todos that claude might be using:

  ⏺ Update Todos
    ⎿  ☒ Update task-003 status to In Progress
       ☒ Analyze project requirements and design database schema
       ☒ Set up SQLite database infrastructure
       ☐ Create comprehensive test suite (unit, integration, performance)

- claude runs into the ame issue more than once

- claude shows signs of frustration

  

If the above conditions are met then this doesn't mean we should stop and reflect. But it's a good point in time to look back since the previous reflection, and the complexity of what is currently being worked on, in order to determine if we should stop and reflect, or not before continuing.

For example, if we are working on something trivial with not much uncertainty and a clear path forward then do not stop and reflect. If we are working on something where the path forward is full of landmines, uncertainty, forks in the road, various strategies and unclear direction then this is a good point in time to stop and reflect.

---

## Step 1: Assess Current State

- What has been changed so far?
- What is the current state of development?
- Are you still aligned with the original task intent?

---

## Step 2: Clarify Next Steps

Ask yourself:

- Are the next steps clear?
- If not, define **2–3 potential paths** to move forward.
- Choose the option(s) that help complete the task **without compromising the milestone**, if one exists.

---

## Step 3: Align with Milestones or Project Direction

- **If the task belongs to a milestone**: Ensure progress stays aligned with the milestone's goals.
- **If the task is standalone**: Apply the same reflective thinking to ensure your decisions align with the **project's overall direction**.

---

## Step 4: Current State

### Locate the `state/` Directory

1. Look inside:  

   ```
   viscera/descriptions/structured/state/
   ```

2. If not found, search elsewhere in `viscera/descriptions/structured/`.

3. If multiple `state/` folders exist, **use the one closest to** `viscera/descriptions/`.

### Create a New State File

1. Use the current date and time to name the file in this format:  

   ```
   YYYYMMDD_hhmmss.md
   ```

   Example:  
   `20250701_140000.md` for July 1, 2025 at 2:00 PM

2. Inside the file, use the following structure:

   ```markdown
   # State of the Task (Put task name & reference to task here)
   
   (Your reflection here)
   
   # State of the Milestone (Put milestone name & reference to milestone here)
   
   (Your reflection here)
   
   # State of the Project (Put project name & reference to task here)
   
   (Your reflection here)
   ```

3. **Ultrathink** before writing. The purpose of the file is to:

   - Allow **backtracking** if mistakes are made.
   - Track the **pace and evolution** of the task, milestone, and project.
   - Help programmers or LLMs **diagnose development bottlenecks or stagnation**.

4. Once your thoughts are clear, write them into the file.  
   File naming is timestamp-based, so **conflicts should never occur**.

---

## Philosophy

This practice encourages intentionality, clarity, and adaptability—key to avoiding aimless coding and ensuring each step contributes meaningfully to project goals.