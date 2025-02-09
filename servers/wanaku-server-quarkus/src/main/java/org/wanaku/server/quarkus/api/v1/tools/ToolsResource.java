package org.wanaku.server.quarkus.api.v1.tools;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.jboss.logging.Logger;
import org.wanaku.api.types.ToolReference;

@ApplicationScoped
@Path("/api/v1/tools")
public class ToolsResource {
    private static final Logger LOG = Logger.getLogger(ToolsResource.class);

    @Inject
    ToolsBean toolsBean;

    @Path("/add")
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    public Response add(ToolReference resource) {
        try {
            toolsBean.add(resource);
            return Response.ok().build();
        } catch (Exception e) {
            LOG.errorf("Failed to add tools %s: %s", resource.getName(), e.getMessage(), e);
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity("Failed to expose tool").build();
        }
    }
}
