package concurrent;

import es.bsc.compss.types.annotations.Constraints;
import es.bsc.compss.types.annotations.Parameter;
import es.bsc.compss.types.annotations.parameter.Direction;
import es.bsc.compss.types.annotations.parameter.Type;
import es.bsc.compss.types.annotations.task.Method;

public interface ConcurrentMItf {

	@Constraints(computingUnits = "1")
	@Method(declaringClass = "concurrent.ConcurrentMImpl")
	void plusone(
		@Parameter(type = Type.FILE, direction = Direction.CONCURRENT) String fileName
	);
}
