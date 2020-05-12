/*
 *  Copyright 2002-2019 Barcelona Supercomputing Center (www.bsc.es)
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 */
package es.bsc.compss.types.request.ap;

import es.bsc.compss.components.impl.AccessProcessor;
import es.bsc.compss.components.impl.DataInfoProvider;
import es.bsc.compss.components.impl.TaskAnalyser;
import es.bsc.compss.components.impl.TaskDispatcher;
import es.bsc.compss.types.Application;
import es.bsc.compss.types.Barrier;
import es.bsc.compss.worker.COMPSsException;
import java.util.concurrent.Semaphore;


public class EndOfAppRequest extends APRequest implements Barrier {

    private final Application app;
    private final Semaphore sem;


    /**
     * Creates a new request to end the application.
     * 
     * @param app Application Id.
     * @param sem Waiting semaphore.
     */
    public EndOfAppRequest(Application app, Semaphore sem) {
        this.app = app;
        this.sem = sem;
    }

    /**
     * Returns the application of the request.
     * 
     * @return The application of the request.
     */
    public Application getApp() {
        return this.app;
    }

    /**
     * Returns the waiting semaphore of the request.
     * 
     * @return The waiting semaphore of the request.
     */
    public Semaphore getSemaphore() {
        return this.sem;
    }

    @Override
    public void process(AccessProcessor ap, TaskAnalyser ta, DataInfoProvider dip, TaskDispatcher td) {
        ta.noMoreTasks(this);
    }

    @Override
    public APRequestType getRequestType() {
        return APRequestType.END_OF_APP;
    }

    @Override
    public void setException(COMPSsException exception) {
        // EndOfApp does not support exceptions.
    }

    @Override
    public COMPSsException getException() {
        // EndOfApp does not support exceptions.
        return null;
    }

    @Override
    public void release() {
        sem.release();
    }

}
