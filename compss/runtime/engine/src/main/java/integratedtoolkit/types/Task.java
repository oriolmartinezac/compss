package integratedtoolkit.types;

import integratedtoolkit.types.parameter.Parameter;
import integratedtoolkit.types.allocatableactions.ExecutionAction;
import integratedtoolkit.types.colors.ColorConfiguration;
import integratedtoolkit.types.colors.ColorNode;
import integratedtoolkit.types.implementations.Implementation.TaskType;

import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;


public class Task implements Comparable<Task> {

    // Task ID management
    private static final int FIRST_TASK_ID = 1;
    private static AtomicInteger nextTaskId = new AtomicInteger(FIRST_TASK_ID);


    // Task states
    public enum TaskState {
        TO_ANALYSE, 
        TO_EXECUTE, 
        FINISHED, 
        FAILED
    }


    // Task fields
    private final long appId;
    private final int taskId;
    private TaskState status;
    private final TaskDescription taskDescription;

    // Data Dependencies
    private final List<Task> predecessors;
    private final List<Task> successors;

    // Scheduling info
    private Task enforcingTask;
    private final List<ExecutionAction<?, ?>> executions;
    
    // Execution count information
    private int executionCount;


    public Task(Long appId, String methodClass, String methodName, boolean isPrioritary, int numNodes, boolean isReplicated, 
            boolean isDistributed, boolean hasTarget, Parameter[] parameters) {
        
        this.appId = appId;
        this.taskId = nextTaskId.getAndIncrement();
        this.status = TaskState.TO_ANALYSE;
        this.taskDescription = new TaskDescription(methodClass, methodName, isPrioritary, numNodes, isReplicated, isDistributed, 
                                                    hasTarget, parameters);
        this.predecessors = new LinkedList<>();
        this.successors = new LinkedList<>();
        this.executions = new LinkedList<>();
    }

    public Task(Long appId, String namespace, String service, String port, String operation, boolean isPrioritary, boolean hasTarget,
            Parameter[] parameters) {

        this.appId = appId;
        this.taskId = nextTaskId.getAndIncrement();
        this.status = TaskState.TO_ANALYSE;
        this.taskDescription = new TaskDescription(namespace, service, port, operation, isPrioritary, hasTarget, parameters);
        this.predecessors = new LinkedList<>();
        this.successors = new LinkedList<>();
        this.executions = new LinkedList<>();
    }

    public static int getCurrentTaskCount() {
        return nextTaskId.get();
    }

    public void addDataDependency(Task producer) {
        producer.successors.add(this);
        this.predecessors.add(producer);
    }

    public void releaseDataDependents() {
        for (Task t : this.successors) {
            t.predecessors.remove(this);
        }
        this.successors.clear();
    }

    public List<Task> getSuccessors() {
        return successors;
    }

    public List<Task> getPredecessors() {
        return predecessors;
    }

    public long getAppId() {
        return appId;
    }

    public int getId() {
        return taskId;
    }

    public TaskState getStatus() {
        return status;
    }

    public void setStatus(TaskState status) {
        this.status = status;
    }

    public void setEnforcingTask(Task task) {
        this.enforcingTask = task;
    }
    
    public boolean isFree() {
        return (this.executionCount == 0);
    }
    
    public void setExecutionCount(int executionCount) {
        this.executionCount = executionCount;
    }
    
    public void decreaseExecutionCount() {
        --this.executionCount;
    }

    public TaskDescription getTaskDescription() {
        return taskDescription;
    }

    public boolean isSchedulingForced() {
        return this.enforcingTask != null;
    }

    public Task getEnforcingTask() {
        return this.enforcingTask;
    }

    public String getDotDescription() {
        int monitorTaskId = taskDescription.getId() + 1; // Coherent with Trace.java
        ColorNode color = ColorConfiguration.COLORS[monitorTaskId % ColorConfiguration.NUM_COLORS];

        String shape;
        if (taskDescription.getType() == TaskType.METHOD) {
            if (this.taskDescription.isReplicated()) {
                shape = "doublecircle";
            } else if (this.taskDescription.isDistributed()) {
                // Its only a scheduler hint, no need to show them differently
                shape = "circle";
            } else {
                shape = "circle";
            }
        } else { // Service
            shape = "diamond";
        }
        // TODO: Future Shapes "triangle" "square" "pentagon"

        return getId() + "[shape=" + shape + ", " + "style=filled fillcolor=\"" + color.getFillColor() + "\" fontcolor=\""
                + color.getFontColor() + "\"];";
    }

    public String getLegendDescription() {
        StringBuilder information = new StringBuilder();
        information.append("<tr>").append("\n");
        information.append("<td align=\"right\">").append(this.getMethodName()).append("</td>").append("\n");
        information.append("<td bgcolor=\"").append(this.getColor()).append("\">&nbsp;</td>").append("\n");
        information.append("</tr>").append("\n");

        return information.toString();
    }

    public String getMethodName() {
        String methodName = taskDescription.getName();
        return methodName;
    }

    public String getColor() {
        int monitorTaskId = taskDescription.getId() + 1; // Coherent with Trace.java
        ColorNode color = ColorConfiguration.COLORS[monitorTaskId % ColorConfiguration.NUM_COLORS];
        return color.getFillColor();
    }

    public void addExecution(ExecutionAction<?, ?> execution) {
        this.executions.add(execution);
    }

    public List<ExecutionAction<?, ?>> getExecutions() {
        return executions;
    }

    // Comparable interface implementation
    @Override
    public int compareTo(Task task) {
        if (task == null) {
            throw new NullPointerException();
        }

        return this.getId() - task.getId();
    }

    @Override
    public boolean equals(Object o) {
        return (o instanceof Task) && (this.taskId == ((Task) o).taskId);
    }

    @Override
    public int hashCode() {
        return super.hashCode();
    }

    @Override
    public String toString() {
        StringBuilder buffer = new StringBuilder();

        buffer.append("[[Task id: ").append(getId()).append("]");
        buffer.append(", [Status: ").append(getStatus()).append("]");
        buffer.append(", ").append(getTaskDescription().toString()).append("]");

        return buffer.toString();
    }

}
