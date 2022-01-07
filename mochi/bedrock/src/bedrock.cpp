/*
 * (C) 2018 The University of Chicago
 *
 * See COPYRIGHT in top-level directory.
 */
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <bedrock/Client.hpp>
#include <bedrock/ServiceHandle.hpp>
#include <bedrock/Exception.hpp>

namespace py11 = pybind11;
using namespace pybind11::literals;
using namespace bedrock;

struct margo_instance;
typedef struct margo_instance* margo_instance_id;
typedef py11::capsule pymargo_instance_id;

#define MID2CAPSULE(__mid)   py11::capsule((void*)(__mid), "margo_instance_id", nullptr)
#define CAPSULE2MID(__caps)  (margo_instance_id)(__caps)

PYBIND11_MODULE(_pybedrock, m) {
    m.doc() = "Bedrock client C++ extension";
    py11::register_exception<Exception>(m, "Exception", PyExc_RuntimeError);
    py11::class_<Client>(m, "Client")
        .def(py11::init<pymargo_instance_id>())
        .def("create_service_handle",
             &Client::makeServiceHandle,
             "Create a ServiceHandle instance",
             "address"_a,
             "provider_id"_a=0);
    py11::class_<ServiceHandle>(m, "ServiceHandle")
        .def("get_config",
             [](const ServiceHandle& sh) {
                std::string config;
                sh.getConfig(&config);
                return std::move(config);
             })
        .def("query_config",
            [](const ServiceHandle& sh, const std::string& script) {
                std::string result;
                sh.queryConfig(script, &result);
                return std::move(result);
            }, "script"_a)
        .def("add_ssg_group", [](const ServiceHandle& sh, const std::string& config) {
                sh.addSSGgroup(config);
            },
            "config"_a)
        .def("create_abtio_instance",
            [](const ServiceHandle& sh,
               const std::string& name,
               const std::string& pool,
               const std::string& config) {
                    sh.createABTioInstance(name, pool, config);
            }, "name"_a, "pool"_a, "config"_a = std::string("{}"))
        .def("load_module",
            [](const ServiceHandle& sh,
               const std::string& name,
               const std::string& path) {
                    sh.loadModule(name, path);
            }, "name"_a, "path"_a)
        .def("start_provider",
            [](const ServiceHandle& sh,
               const std::string& name,
               const std::string& type,
               uint16_t provider_id,
               const std::string& pool,
               const std::string& config,
               const DependencyMap& deps) {
                    sh.startProvider(name, type, provider_id, pool, config, deps);
            }, "name"_a, "type"_a, "provider_id"_a=0, "pool"_a=std::string(""),
             "config"_a=std::string("{}"),
             "dependencies"_a=DependencyMap())
        .def("create_client",
            [](const ServiceHandle& sh,
               const std::string& name,
               const std::string& type,
               const std::string& config,
               const DependencyMap& deps) {
                    sh.createClient(name, type, config, deps);
            }, "name"_a, "type"_a, "config"_a=std::string("{}"),
             "dependencies"_a=DependencyMap())
    ;
}
